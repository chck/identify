# -*- coding: utf-8 -*-
from seeking.medias.twitter.api import Twitter
from seeking.utils.data_utils.datastore.twitter import Users, Tweets


def crawl_tweets(screen_name: str):
    user_id = crawl_user(screen_name)
    tweets = Tweets()
    tweets.bulk_upsert(Twitter().get_tweets(screen_name), user_id=user_id)
    return user_id


def crawl_user(screen_name: str):
    user = Twitter().get_user(screen_name)
    users = Users()
    users.upsert(user.__dict__, id=user.id)
    return user.id


def delete_user(screen_name: str):
    user = Twitter().get_user(screen_name)
    Users().delete(user.id)
    tweets = Tweets()
    _tweets, _ = tweets.find_all(user_id=user.id)
    tweet_ids = [t.id for t in _tweets]
    tweets.bulk_delete(tweet_ids, user_id=user.id)
    return user.id


if __name__ == '__main__':
    crawl_tweets('masason')
