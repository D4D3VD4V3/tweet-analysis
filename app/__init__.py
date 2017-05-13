import os

from celery import Celery
from flask import Flask, render_template
from flask_assets import Environment, Bundle
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Link
from config import config_dict

secret_key = os.getenv("SECRET_KEY")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
FLASK_CONFIGURATION = os.getenv("FLASK_CONFIGURATION", "dev")
NUMBER_OF_TWEETS = int(os.getenv("NUMBER_OF_TWEETS", config_dict[FLASK_CONFIGURATION].NUMBER_OF_TWEETS))

celery = Celery(__name__, backend=os.getenv("RABBITMQ_BIGWIG_RX_URL"), broker=os.getenv("RABBITMQ_BIGWIG_TX_URL"))
topbar = Navbar(View("Home", "bp.home"), Link("Source Code", r"http://www.github.com/d4d3vd4v3/tweet-analysis"))
nav = Nav()
nav.register_element("topbar", topbar)


def make_celery(app):
    global celery
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(config_dict[FLASK_CONFIGURATION])
    app.secret_key = secret_key
    Bootstrap(app)
    assets = Environment(app)
    js_files = Bundle('justgage.js', 'raphael-2.1.4.min.js', filters='rjsmin', output='gen/minified.js')
    assets.register('js_files', js_files)
    nav.init_app(app)
    from .blueprints import bp
    app.register_blueprint(bp)
    global celery
    celery = make_celery(app)

    @app.errorhandler(404)
    def fournotfour(_):
        return render_template("404page.html"), 404

    @app.errorhandler(500)
    def fivezerozero(_):
        return render_template("500page.html"), 500
    return app
