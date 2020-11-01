# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models import BaseFileConfig, ConcurrencySettings, KafkaSettings


@dataclasses.dataclass
class WriterSettings(BaseFileConfig):
    """ WriterSettings represents settings of writer component. """

    kafka: KafkaSettings
    concurrency: ConcurrencySettings

    # kafka topic is processed once per this interval
    # leave this interval empty for single check
    interval: typing.Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, typing.Any]) -> WriterSettings
        # kafka config is provided as a path to the file
        kafka_config = KafkaSettings.from_dict(cls._load_file_data(data["kafka_config_path"]))

        # client and group are mandatory for consumer
        assert kafka_config.client, "Client must be set"
        assert kafka_config.group, "Group must be set"

        concurrency = ConcurrencySettings.from_dict(data["concurrency"])

        interval = data.get("interval")
        if not interval or interval < 1:
            interval = None

        return WriterSettings(
            kafka=kafka_config,
            concurrency=concurrency,
            interval=interval,
        )
