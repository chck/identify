# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
from typing import List

from dataclasses import dataclass
from flask import current_app as app
from tweepy import (
    OAuthHandler, API, Cursor
)

from seeking.medias.twitter.utils import Token


@dataclass
class Tweet:
    id: int
    user_id: int
    screen_name: str
    text: str
    source: str
    geo: str
    coordinates: str
    place: str
    created_at: datetime


@dataclass
class User:
    id: int
    name: str
    screen_name: str
    description: str
    followers_count: int
    friends_count: int
    listed_count: int
    created_at: datetime
    favourites_count: int
    geo_enabled: bool
    verified: bool
    statuses_count: int
    profile_background_color: str
    profile_background_image_url: str
    profile_image_url: str
    profile_link_color: str
    profile_sidebar_border_color: str
    profile_sidebar_fill_color: str
    profile_text_color: str
    following: bool
    follow_request_sent: bool
    notifications: bool
    updated_at: datetime


class Twitter:
    def __init__(self, token: Token = None):
        self.api = self.set_token(token)

    def set_token(self, token: Token = None):
        auth = OAuthHandler(
            consumer_key=token.consumer_key if token else app.config['CONSUMER_KEY'],
            consumer_secret=token.consumer_secret if token else app.config['CONSUMER_SECRET'],
        )
        auth.set_access_token(
            key=token.access_token if token else app.config['ACCESS_TOKEN'],
            secret=token.access_token_secret if token else app.config['ACCESS_TOKEN_SECRET'],
        )
        return API(auth)

    def get_user(self, screen_name: str):
        user = self.api.get_user(screen_name)
        return User(
            id=int(user.id_str),
            name=user.name,
            screen_name=user.screen_name,
            description=user.description,
            followers_count=user.followers_count,
            friends_count=user.friends_count,
            listed_count=user.listed_count,
            created_at=user.created_at,
            favourites_count=user.favourites_count,
            geo_enabled=user.geo_enabled,
            verified=user.verified,
            statuses_count=user.statuses_count,
            profile_background_color=user.profile_background_color,
            profile_background_image_url=user.profile_background_image_url,
            profile_image_url=user.profile_image_url,
            profile_link_color=user.profile_link_color,
            profile_sidebar_border_color=user.profile_sidebar_border_color,
            profile_sidebar_fill_color=user.profile_sidebar_fill_color,
            profile_text_color=user.profile_text_color,
            following=user.following,
            follow_request_sent=user.follow_request_sent,
            notifications=user.notifications,
            updated_at=datetime.now(),
        )

    def get_tweets(self, screen_name: str) -> List[Tweet]:
        return [Tweet(
            id=int(status.id_str),
            user_id=int(status.author.id_str),
            screen_name=screen_name,
            text=status.text,
            source=status.source,
            geo=status.geo,
            coordinates=status.coordinates,
            place=status.place,
            created_at=status.created_at,
        ) for status in Cursor(self.api.user_timeline,
                               screen_name=screen_name,
                               count=200,
                               include_rts=False,
                               trim_user=True,
                               exclude_replies=True).items()]


if __name__ == '__main__':
    from seeking.config.config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

    file_path = Path(__file__).resolve().parent / '..' / '..' / 'config' / 'config.yml'
    api = Twitter(Token(consumer_key=CONSUMER_KEY,
                        consumer_secret=CONSUMER_SECRET,
                        access_token=ACCESS_TOKEN,
                        access_token_secret=ACCESS_TOKEN_SECRET)).api
    screen_name = 'masason'
    x = api.user_timeline(screen_name)
    print(x[0])
