# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models import BaseDto


@dataclasses.dataclass
class CheckResult(BaseDto):
    """ CheckResult contains result of checking one website. """

    # website url; also an id
    url: str

    # check duration in seconds
    duration: float

    # str representation of an error if there was any
    error: typing.Optional[str] = None

    # whether or not regex was found (None in case there isn't regex for this website)
    pattern_found: typing.Optional[bool] = None

    # http status; empty in case of timeout
    status_code: typing.Optional[int] = None
