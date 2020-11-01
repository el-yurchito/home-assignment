# -*- coding: utf-8 -*-
import json
import typing

from shared.models.base_dto import BaseDto


class BaseFileConfig(BaseDto):
    """ Base class for file (json) configs. """

    @classmethod
    def import_from_file(cls, file_path):
        """ Creates and returns new instance based on json data imported from file. """
        return cls.from_dict(cls._load_file_data(file_path))

    @classmethod
    def _load_file_data(cls, file_path):
        # type: (str) -> typing.Mapping[str, typing.Any]
        with open(file_path, "r") as f:
            return json.load(f)
