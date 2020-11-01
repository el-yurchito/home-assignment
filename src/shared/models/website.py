# -*- coding: utf-8 -*-
import dataclasses
import re
import typing

from shared.models.base_dto import BaseDto

_DEFAULT_TIMEOUT = 5


@dataclasses.dataclass
class WebsiteSettings(BaseDto):
    """ Website availability checking settings. """

    url: str  # website url; also an id
    regex: typing.Optional[bytes] = None  # if this parameter is empty then no regex check will be made
    timeout: typing.Optional[float] = None  # if this parameter is empty then default timeout will be used

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, typing.Any]) -> WebsiteSettings
        regex = data.get("regex")
        if regex:
            regex = regex.encode("utf8")  # transform to bytes to use on bytes responses
            re.compile(regex)  # pattern validation
        else:
            regex = None

        return WebsiteSettings(
            url=data["url"],
            regex=regex,
            timeout=data.get("timeout") or _DEFAULT_TIMEOUT,
        )
