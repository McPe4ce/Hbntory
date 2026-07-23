from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    """Creates the app, loads the config and binds it to the DB"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app