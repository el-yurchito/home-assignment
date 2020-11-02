# -*- coding: utf-8 -*-
import os

from writer.worker import Worker

config_file_path = os.environ.get("WRITER_CONFIG", "./writer/config.json")
worker = Worker(config_file_path)
worker.run()
