# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models.base_dto import BaseDto

_DEFAULT_CONCURRENT_CHECKS = 4
_DEFAULT_CONCURRENT_TIMEOUT = 60


@dataclasses.dataclass
class ConcurrencySettings(BaseDto):
    """ Settings for running tasks in parallel. """

    # maximum amount of checks running at the same time
    # if this parameter is empty then default concurrency limit will be used
    # set value to 1 in order to turn off parallel launching
    checks: int

    # common timeout (seconds) for all tasks launched concurrently
    # if this parameter is empty then default concurrency timeout will be used
    timeout: float

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, typing.Optional[typing.Union[int, float]]]) -> ConcurrencySettings
        checks = data.get("checks")
        if not checks or checks < 0:  # there should be at least one check at a time
            checks = _DEFAULT_CONCURRENT_CHECKS

        timeout = data.get("timeout")
        if not timeout or timeout < 0:
            timeout = _DEFAULT_CONCURRENT_TIMEOUT

        return ConcurrencySettings(
            checks=checks,
            timeout=timeout,
        )
