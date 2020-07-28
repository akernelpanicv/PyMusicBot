from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

from py_music_bot.routes import init_routes
from .models import init_db


def create_app(*args, **kwargs):
    app = Flask(__name__)
    app.config.from_envvar('PyMusicBot_SETTINGS')

    init_extensions(app, *args, **kwargs)

    return app


def init_extensions(app, test_mode=False):
    init_db(app)
    init_routes(app)

    Cache(app, config={
        'CACHE_TYPE': 'simple',
    })

    if not test_mode:
        CSRFProtect(app)


app = create_app()

__all__ = [
    'app',
    'create_app',
]
