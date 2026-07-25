from flask import Flask
from app.config import Config
from app.extensions import db
from app.auth.routes import auth_bp
from app.admin.routes import admin_bp

def create_app():
    """Creates the app, loads the config and binds it to the DB"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    return app