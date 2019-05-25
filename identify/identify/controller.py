# -*- coding: utf-8 -*-
from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    request,
    current_app as app,
)

from identify import logger
from identify import tasks
from identify.medias.twitter.service import crawl_user, delete_user as _delete_user
from identify.preprocessing.text import (
    nounize, discover_keywords, _generate_wordcloud, generate_wordclouds, vectorize
)
from identify.utils.data_utils.datastore.twitter import Users, Tweets, Replies

api = Blueprint('api', __name__)


@api.route("/")
def index():
    """help apis"""
    funcs = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            funcs[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(funcs), 200


@api.route("/twitter/users")
@api.route("/twitter/users/<screen_name>")
def users(screen_name=None):
    """crawl twitter user"""
    if screen_name:
        entity = Users().find(crawl_user(screen_name))
        return jsonify({
            'data': entity,
        }), 200
    else:
        limit = request.args.get('limit', type=int)
        cursor = request.args.get('cursor', type=str)
        if cursor:
            cursor = cursor.encode(encoding='utf-8')
        entity, next_cursor = Users().find_all(limit=limit,
                                               cursor=cursor)
        return jsonify({
            'data': entity,
            'next_cursor': next_cursor,
            'limit': limit,
        }), 200


@api.route("/twitter/users/<screen_name>/delete")
def delete_user(screen_name):
    """crawl twitter user"""
    return jsonify({
        'deleted': _delete_user(screen_name)
    }), 200


@api.route("/twitter/tweets/<screen_name>")
def tweets(screen_name):
    """crawl twitter tweets"""
    limit = request.args.get('limit', type=int)
    cursor = request.args.get('cursor', type=str)
    if cursor:
        cursor = cursor.encode(encoding='utf-8')

    entity, next_cursor = Tweets().find_all(user_id=crawl_user(screen_name),
                                            limit=limit,
                                            cursor=cursor)

    return jsonify({
        'data': entity,
        'next_cursor': next_cursor,
        'limit': limit,
    }), 200


@api.route("/twitter/replies/<screen_name>")
def replies(screen_name):
    """crawl twitter replies"""
    limit = request.args.get('limit', type=int)
    cursor = request.args.get('cursor', type=str)
    if cursor:
        cursor = cursor.encode(encoding='utf-8')

    entity, next_cursor = Replies().find_all(user_id=crawl_user(screen_name),
                                             limit=limit,
                                             cursor=cursor)

    return jsonify({
        'data': entity,
        'next_cursor': next_cursor,
        'limit': limit,
    }), 200


@api.route("/crawl/<screen_name>")
def kick_crawling(screen_name: str):
    """kick crawling task"""
    module = request.args.get('module')

    logger.info('kick crawling (screen_name: {})'.format(screen_name))
    q = tasks.get_crawling_queue()
    q.enqueue(tasks.process_crawling, screen_name, module)

    return jsonify({
        'code': 200,
        'message': 'kicked crawling (screen_name: {}) at {}'.format(screen_name, datetime.now()),
    }), 200
