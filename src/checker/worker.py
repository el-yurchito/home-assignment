# -*- coding: utf-8 -*-
from concurrent import futures
from datetime import datetime
import dataclasses
import json
import re
import time
import typing

import kafka
import requests

from checker.models import CheckerSettings, AvailabilityCheckResult
from shared.models import WebsiteSettings


class Worker(object):
    """ Worker is website availability check workflow. """

    def __init__(self, config_file_path):
        # type: (str) -> None
        self.config = CheckerSettings.import_from_file(config_file_path)  # type: CheckerSettings
        # copied from `getting started with kafka`
        self.producer = kafka.KafkaProducer(
            bootstrap_servers=self.config.kafka.bootstrap_servers,
            security_protocol="SSL",
            ssl_cafile=self.config.kafka.ssl_ca_file,
            ssl_certfile=self.config.kafka.ssl_cert_file,
            ssl_keyfile=self.config.kafka.ssl_key_file,
        )

    def run(self):
        if self.config.concurrent_checks == 1:
            run_method = self._run_single_thread
        else:
            run_method = self._run_thread_pool

        while True:
            run_method()
            if self.config.interval:
                time.sleep(self.config.interval)
            else:
                # do exactly one check if no interval is specified
                break

    def _run_single_thread(self):
        for website in self.config.websites:
            exc = self._check_and_publish(website)
            if exc is not None:
                raise exc

    def _run_thread_pool(self):
        errors = []
        with futures.ThreadPoolExecutor(max_workers=self.config.concurrent_checks) as executor:
            # got this from docs.python.org
            future_tasks = [executor.submit(self._check_and_publish, website)
                            for website in self.config.websites]

            # launch parallel checks and ignore errors
            # but raise them later
            for task in futures.as_completed(future_tasks, timeout=self.config.concurrent_timeout):
                task_result = task.result()
                if task_result is not None:
                    errors.append(task_result)

        if errors:
            errors_str = "\n".join([str(exc) for exc in errors])
            raise RuntimeError(f"{len(errors)} occurred during website checks:\n{errors_str}")

    def _check_and_publish(self, website):
        # type: (WebsiteSettings) -> typing.Optional[Exception]
        """
        Makes website check and publishes result to kafka.
        Captures any exception but returns is as a result for further handling.
        """
        try:
            check_result = self._check_website(website)
            serialized = json.dumps(dataclasses.asdict(check_result)).encode("utf8")  # serialize dto to bytes

            future = self.producer.send(self.config.kafka.topic, serialized)
            record_meta = future.get(timeout=self.config.kafka.timeout_send)
        except Exception as exc:
            error = exc
        else:
            error = None

        return error

    @classmethod
    def _check_website(cls, website):
        # type: (WebsiteSettings) -> AvailabilityCheckResult
        """
        Checking of single website.

        Handles checking-related exceptions, such as those
        which can be raised while getting response
        from website (e,g. timeout or network problems).

        Other exceptions are propagated.
        """

        # if it's not necessary to check if response contains regex pattern
        # then it's ok to use HEAD method since there's no need in response body
        if website.regex:
            method = requests.get
        else:
            method = requests.head

        # measure time because it's not for sure that there will be response at all
        call_started = datetime.now()
        try:
            # call GET or HEAD
            response = method(website.url, timeout=website.timeout)
        except (IOError, requests.RequestException) as exc:
            error = str(exc)
            response = getattr(exc, "response", None)
        else:
            error = None
        call_finished = datetime.now()

        if response is not None:
            response_content = response.content
            status_code = response.status_code
        else:
            response_content = status_code = None

        # do regex matching
        if website.regex and response_content:
            pattern_found = re.search(website.regex, response_content) is not None
        else:
            pattern_found = None

        return AvailabilityCheckResult(
            duration=(call_finished - call_started).total_seconds(),
            error=error,
            pattern_found=pattern_found,
            status_code=status_code,
        )
