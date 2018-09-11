# -*- coding: utf-8 -*-
from typing import Optional

import yaml
from dataclasses import dataclass


@dataclass
class Token:
    consumer_key: Optional[str] = None
    consumer_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None

    def from_yml(self, file_path: str):
        config = yaml.load(open(file_path, 'r'))['twitter']
        return Token(
            consumer_key=config['consumer_key'],
            consumer_secret=config['consumer_secret'],
            access_token=config['access_token'],
            access_token_secret=config['access_token_secret']
        )
