# -*- coding: utf-8 -*-
import dataclasses
import typing

from shared.models.base_dto import BaseDto

_DEFAULT_PAGE_SIZE = 100


@dataclasses.dataclass
class PostgresqlSettings(BaseDto):

    # full connection string, like `postgres://user:password@host:port/db_name?param1=val1`
    connection_string: str = ""

    # maximum size of single insert batch
    # if this value isn't provided, then default value will be used
    page_size: typing.Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        # type: (typing.Mapping[str, str]) -> PostgresqlSettings
        connection_string = data["connection_string"]

        page_size = data.get("page_size")
        if not page_size or page_size < 1:
            page_size = _DEFAULT_PAGE_SIZE

        return PostgresqlSettings(
            connection_string=connection_string,
            page_size=page_size,
        )
