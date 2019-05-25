# -*- coding: utf-8 -*-
from identify.medias.twitter.api import Twitter
from identify.utils.data_utils.datastore.twitter import (
    Users, Tweets, fetch_all_tweets
)
from identify.utils.data_utils.datastore.twitter.preprocessed_tweets import PreprocessedTweets, fetch_all_parsed_tweets
from identify.utils.data_utils.datastore.twitter.preprocessed_users import PreprocessedUsers
from identify.utils.data_utils.datastore.twitter.replies import Reply, Replies


def crawl_tweets(screen_name: str):
    user_id = crawl_user(screen_name)
    tweets = Tweets()
    tweets.bulk_upsert(Twitter().get_tweets(screen_name), user_id=user_id)
    return user_id


def crawl_replies(screen_name: str):
    user_id = crawl_user(screen_name)
    replies = [Reply(
        id=reply.id,
        user_id=reply.user_id,
        screen_name=reply.screen_name,
        target_text=root.text,
        source_text=reply.text,
        created_at=reply.created_at,
    ) for (root, reply) in Twitter().get_replies(screen_name)]
    model = Replies()
    model.bulk_upsert(replies, user_id=user_id)
    return user_id


def crawl_user(screen_name: str):
    user = Twitter().get_user(screen_name)
    users = Users()
    users.upsert(user.__dict__, id=user.id)
    return user.id


def delete_user(screen_name: str):
    user = Twitter().get_user(screen_name)
    Users().delete(user.id)
    PreprocessedUsers().delete(user.id)

    tweet_ids = [int(t['id']) for t in fetch_all_tweets(user.id)]
    Tweets().bulk_delete(tweet_ids, user_id=user.id)

    tweet_ids = [int(t['id']) for t in fetch_all_parsed_tweets(user.id)]
    PreprocessedTweets().bulk_delete(tweet_ids, user_id=user.id)

    return user.id


if __name__ == '__main__':
    crawl_tweets('masason')
