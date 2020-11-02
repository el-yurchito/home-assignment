# -*- coding: utf-8 -*-
import dataclasses
import re
import typing

from shared.models.base_dto import BaseDto

_DEFAULT_TIMEOUT = 5


@dataclasses.dataclass
class WebsiteCheckSettings(BaseDto):
    """ Website availability checking settings. """

    url: str  # website url; also an id
    regex: typing.Optional[bytes] = None  # if this parameter is empty then no regex check will be made
    timeout: typing.Optional[float] = None  # if this parameter is empty then default timeout will be used

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, typing.Any]) -> WebsiteCheckSettings
        regex = data.get("regex")
        if regex:
            regex = regex.encode("utf8")  # transform to bytes to use on bytes responses
            re.compile(regex)  # pattern validation
        else:
            regex = None

        return WebsiteCheckSettings(
            url=data["url"],
            regex=regex,
            timeout=data.get("timeout") or _DEFAULT_TIMEOUT,
        )


@dataclasses.dataclass
class WebsiteWriteSettings(BaseDto):
    """ WebsiteWriteSettings can tell DB table website metrics should be written to. """

    url: str  # website url; also an id
    table_name: str

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, str]) -> WebsiteWriteSettings
        return WebsiteWriteSettings(**data)
