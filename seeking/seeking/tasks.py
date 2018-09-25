# -*- coding: utf-8 -*-
import psq
from flask import current_app as app
from google.cloud import pubsub

from seeking import logger
from seeking.medias.twitter.service import crawl_tweets, crawl_replies


def get_crawling_queue():
    publisher_client = pubsub.PublisherClient()
    subscriber_client = pubsub.SubscriberClient()

    return psq.Queue(publisher_client,
                     subscriber_client,
                     project=app.config['PROJECT_ID'],
                     name='crawling',
                     extra_context=app.app_context)


def process_crawling(screen_name: str, module=None):
    logger.info('crawling is started (screen_name: {})'.format(screen_name))
    if module == 'reply':
        crawl_replies(screen_name)
    else:
        crawl_tweets(screen_name)
