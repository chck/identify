# -*- coding: utf-8 -*-
from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    current_app as app,
)

from seeking import logger
from seeking import tasks
from seeking.medias.twitter.service import crawl_user, crawl_tweets, delete_user as _delete_user
from seeking.utils.data_utils.datastore.twitter import Users, Tweets

api = Blueprint('api', __name__)


@api.route("/")
def index():
    """help apis"""
    funcs = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            funcs[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(funcs), 200


@api.route("/twitter/users/")
@api.route("/twitter/users/<screen_name>")
def users(screen_name=None):
    """crawl twitter user"""
    if screen_name:
        entity = Users().find(crawl_user(screen_name))
    else:
        entity, _ = Users().find_all()
    return jsonify(entity), 200


@api.route("/twitter/users/<screen_name>/delete")
def delete_user(screen_name):
    """crawl twitter user"""
    return jsonify({
        'deleted': _delete_user(screen_name)
    }), 200


@api.route("/twitter/tweets/<screen_name>")
def tweets(screen_name):
    """crawl twitter tweets"""
    entity, _ = Tweets().find_all(user_id=crawl_tweets(screen_name))
    return jsonify(entity), 200


@api.route("/crawl/<screen_name>")
def kick_crawling(screen_name: str):
    """kick crawling task"""
    logger.info('kick crawling (screen_name: {})'.format(screen_name))
    q = tasks.get_crawling_queue()
    q.enqueue(tasks.crawl_tweets, screen_name)

    return jsonify({
        'code': 200,
        'message': 'kicked crawling (screen_name: {}) at {}'.format(screen_name, datetime.now()),
    }), 200