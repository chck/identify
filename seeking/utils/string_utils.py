# -*- coding: utf-8 -*-
from os import path


def get_filepath(builtin_file: str) -> str:
    return path.basename(builtin_file)


def get_filename(builtin_file: str) -> str:
    return path.splitext(get_filepath(builtin_file))[0]


def to_camel(snake: str) -> str:
    return snake.title().replace('_', '')
