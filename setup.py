# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

# noinspection SpellCheckingInspection
setup(
    name="home-assignment",
    packages=find_packages(),
    install_requires=install_requires,
    version="0.0.1",
    license="MIT",
    description="Website availability monitoring",
    author="Yuriy Dzyuban",
    author_email="dzyuban.yuri@gmail.com",
    url="https://github.com/el-yurchito/home-assignment",
    keywords=["home", "assignment"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    data_files=[("", ["requirements.txt"])],
)
