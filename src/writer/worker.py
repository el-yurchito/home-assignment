# -*- coding: utf-8 -*-
import concurrent.futures
import json
import typing
import time

from kafka import KafkaConsumer
from psycopg2 import connect
from psycopg2.extras import execute_values

from shared.models import CheckResult
from writer.models import WriterSettings


class Worker(object):
    """ Worker is checking result handling workflow. """

    def __init__(self, config_file_path):
        # type: (str) -> None
        self.config = WriterSettings.import_from_file(config_file_path)  # type: WriterSettings

        # copied from `getting started with kafka`
        # autocommit is disabled so that messages are not lost in case of polling/parsing error
        self.consumer = KafkaConsumer(
            self.config.kafka.topic,
            auto_offset_reset="earliest",
            bootstrap_servers=self.config.kafka.bootstrap_servers,
            client_id=self.config.kafka.client,
            group_id=self.config.kafka.group,
            enable_auto_commit=False,
            security_protocol="SSL",
            ssl_cafile=self.config.kafka.ssl_ca_file,
            ssl_certfile=self.config.kafka.ssl_cert_file,
            ssl_keyfile=self.config.kafka.ssl_key_file,
        )

    def run(self):
        if self.config.concurrency.checks == 1:
            run_method = self._run_single_thread
        else:
            run_method = self._run_thread_pool

        while True:
            messages = self._get_messages()  # requesting messages to process

            try:
                run_method(messages)
            finally:
                # acknowledge kafka that messages are processed
                # some messages can be lost though, due to processing exceptions
                self.consumer.commit()

            if self.config.interval:
                time.sleep(self.config.interval)
            else:
                # do exactly one check if no interval is specified
                break

    def _run_single_thread(self, messages):
        # type: (typing.Mapping[str, typing.List[CheckResult]]) -> None
        """
        Processes websites one by one.
        Fails on the first unhandled exception.
        """

        for website_url, check_results in messages.items():
            exc = self._insert_row_batch(website_url, check_results)
            if exc is not None:
                raise exc

    def _run_thread_pool(self, messages):
        # type: (typing.Mapping[str, typing.List[CheckResult]]) -> None
        """
        Processes websites using thread pool.
        Unhandled exception in one thread doesn't affect other ones,
        but "aggregated" exception containing all unhandled
        exceptions will be raised in the end.
        """

        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.concurrency.checks) as executor:
            future_tasks = [executor.submit(self._insert_row_batch, website, check_results)
                            for website, check_results in messages.items()]

            for task in concurrent.futures.as_completed(future_tasks, timeout=self.config.concurrency.timeout):
                task_result = task.result()
                if task_result is not None:
                    errors.append(task_result)

        if errors:
            errors_str = "\n".join([str(exc) for exc in errors])
            raise RuntimeError(f"{len(errors)} occurred during processing website check results:\n{errors_str}")

    def _get_messages(self):
        # type: () -> typing.Mapping[str, typing.List[CheckResult]]
        """ Receives and decodes chunk of kafka messages. """
        results = {}  # website url to check results map
        for _ in range(2):
            poll_result = self.consumer.poll(
                timeout_ms=self.config.kafka.timeout_poll * 1000,
                max_records=self.config.kafka.poll_max_messages,
            )
            for raw_messages in poll_result.values():
                for raw_message in raw_messages:
                    check_result = CheckResult.from_dict(json.loads(raw_message.value))
                    results.setdefault(check_result.url, []).append(check_result)

        return results

    def _insert_row_batch(self, website_url, check_results):
        # type: (str, typing.List[CheckResult]) -> typing.Optional[Exception]
        """
        Uses settings to find out DB table for given url.
        Inserts check result into this table.
        """

        if not check_results:
            return  # nothing to insert - nothing to do here

        try:
            table_name = self.config.websites_tables[website_url]
        except KeyError as exc:
            raise KeyError(f"DB table settings for url {str(exc)} are not specified")

        try:
            # assume configuration is trusted source
            # otherwise using table_name in sql query like that
            # can lead to SQL injection
            insert_query = f"insert into {table_name} " \
                           f"(url, duration, started_at, error, pattern_found, status_code) " \
                           f"values %s"

            # auto commit if there wasn't any exception
            with connect(self.config.pg.connection_string) as conn:
                with conn.cursor() as cursor:
                    # insert query params
                    values = []
                    for cr in check_results:
                        values.append((cr.url, cr.duration, cr.started_at, cr.error,
                                       cr.pattern_found, cr.status_code))

                    execute_values(cursor, insert_query, values, page_size=self.config.pg.page_size)
        except Exception as exc:
            error = exc
        else:
            error = None

        return error
