# -*- coding: utf-8 -*-
from identify import create_app
from identify import tasks
from identify.config import config

app = create_app(config)

with app.app_context():
    crawling_queue = tasks.get_crawling_queue()

# This is only used when running locally. When running live, gunicorn runs the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
