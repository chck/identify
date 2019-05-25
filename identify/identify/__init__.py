# -*- coding: utf-8 -*-
from logging import INFO, getLogger, StreamHandler
from os import path

from flask import Flask, redirect, url_for, request, jsonify, send_from_directory
from google.cloud import logging, error_reporting

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False


def create_app(config, debug=False, testing=False):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    # https://stackoverflow.com/questions/46319230/using-flasks-jsonify-displays-%C3%A9-as-%C3%83
    app.config['JSON_AS_ASCII'] = False

    app.debug = debug
    app.testing = testing

    # Configure logging
    if not app.testing:
        client = logging.Client(app.config['PROJECT_ID'])
        client.setup_logging(INFO)

    # Register blueprint
    from identify.controller import api
    app.register_blueprint(api, url_prefix='/api')

    # Add a default root route
    @app.route("/")
    def index():
        """redirect api.index"""
        return redirect(url_for('api.index'))

    @app.route("/favicon.ico")
    def favicon():
        """show favicon"""
        return send_from_directory(path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.errorhandler(500)
    def server_error(e):
        client = error_reporting.Client(app.config['PROJECT_ID'])
        client.report_exception(http_context=error_reporting.build_flask_context(request))
        return jsonify({
            'error': {
                'code': 500,
                'message': e.args,
            }
        }), 500

    return app
