# -*- coding: utf-8 -*-
import re
from os import path


def get_filepath(builtin_file: str) -> str:
    return path.basename(builtin_file)


def get_filename(builtin_file: str) -> str:
    return path.splitext(get_filepath(builtin_file))[0]


def to_camel(snake: str) -> str:
    return snake.title().replace('_', '')


def to_snake(camel: str) -> str:
    """https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
