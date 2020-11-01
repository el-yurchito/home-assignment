# -*- coding: utf-8 -*-
import os

from checker.worker import Worker

config_file_path = os.environ.get("CHECKER_CONFIG", "./checker/config.json")
worker = Worker(config_file_path)
worker.run()
