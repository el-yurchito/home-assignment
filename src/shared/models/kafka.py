# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models.base_dto import BaseDto

_DEFAULT_TIMEOUT = 4


@dataclasses.dataclass
class KafkaSettings(BaseDto):
    """ Both kafka producer and consumer connection settings. """

    bootstrap_servers: typing.List[str]
    ssl_ca_file: str
    ssl_cert_file: str
    ssl_key_file: str

    topic: str
    client: typing.Optional[str] = None  # optional for producer
    group: typing.Optional[str] = None  # optional for producer

    # default timeout will be used if these values are empty
    timeout_send: typing.Optional[float] = None
    timeout_poll: typing.Optional[float] = None

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, typing.Any]) -> KafkaSettings
        timeout_send = data.get("timeout_send")
        if not timeout_send or timeout_send < 0:
            timeout_send = _DEFAULT_TIMEOUT

        timeout_poll = data.get("timeout_poll")
        if not timeout_poll or timeout_poll < 0:
            timeout_poll = _DEFAULT_TIMEOUT

        return KafkaSettings(
            bootstrap_servers=data["bootstrap_servers"],
            ssl_ca_file=data["ssl_ca_file"],
            ssl_cert_file=data["ssl_cert_file"],
            ssl_key_file=data["ssl_key_file"],
            topic=data["topic"],
            client=data.get("client"),
            group=data.get("group"),
            timeout_send=timeout_send,
            timeout_poll=timeout_poll,
        )
