# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models import (
    BaseFileConfig, ConcurrencySettings, KafkaSettings,
    PostgresqlSettings, WebsiteWriteSettings,
)


@dataclasses.dataclass
class WriterSettings(BaseFileConfig):
    """ WriterSettings represents settings of writer component. """

    kafka: KafkaSettings
    pg: PostgresqlSettings

    # website writing settings, as provided
    websites: typing.List[WebsiteWriteSettings]

    # website id (url) to table name map
    websites_tables: typing.Mapping[str, str]

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

        # pg config is provided as a path to the file too
        pg = PostgresqlSettings.from_dict(cls._load_file_data(data["pg_config_path"]))

        concurrency = ConcurrencySettings.from_dict(data["concurrency"])

        # use provided website writing settings to make url to table name map
        websites = []
        websites_tables = {}
        for website_cfg in data["websites"]:
            website = WebsiteWriteSettings.from_dict(website_cfg)
            websites.append(website)
            websites_tables[website.url] = website.table_name

        interval = data.get("interval")
        if not interval or interval < 1:
            interval = None

        return WriterSettings(
            kafka=kafka_config,
            pg=pg,
            websites=websites,
            websites_tables=websites_tables,
            concurrency=concurrency,
            interval=interval,
        )
