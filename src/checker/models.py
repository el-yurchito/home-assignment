# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models import BaseDto, BaseFileConfig, ConcurrencySettings, KafkaSettings, WebsiteSettings

_DEFAULT_CONCURRENT_CHECKS = 4
_DEFAULT_CONCURRENT_TIMEOUT = 60


@dataclasses.dataclass
class CheckerSettings(BaseFileConfig):
    """ CheckerSettings represents settings of checker component. """

    kafka: KafkaSettings
    websites: typing.List[WebsiteSettings]
    concurrency: ConcurrencySettings

    # checks are repeated once per this interval
    # leave this interval empty for single check
    interval: typing.Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, typing.Any]) -> CheckerSettings
        # kafka config is provided as a path to the file
        kafka_config = KafkaSettings.from_dict(cls._load_file_data(data["kafka_config_path"]))

        websites = [WebsiteSettings.from_dict(i) for i in data["websites"]]

        concurrency_config = ConcurrencySettings.from_dict(data["concurrency"])

        interval = data.get("interval")
        if not interval or interval < 1:
            interval = None

        return CheckerSettings(
            kafka=kafka_config,
            websites=websites,
            concurrency=concurrency_config,
            interval=interval,
        )


@dataclasses.dataclass
class AvailabilityCheckResult(BaseDto):
    """ AvailabilityCheckResult contains result of checking one website. """

    # check duration in seconds
    duration: float

    # str representation of an error if there was any
    error: typing.Optional[str] = None

    # whether or not regex was found (None in case there isn't regex for this website)
    pattern_found: typing.Optional[bool] = None

    # http status; empty in case of timeout
    status_code: typing.Optional[int] = None
