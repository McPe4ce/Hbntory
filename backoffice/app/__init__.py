from flask import Flask
from app.config import Config
from app.extensions import db
from app.auth.routes import auth_bp
from app.admin.routes import admin_bp
from app.stock.routes import stock_bp
from app.public.routes import public_bp

def create_app():
    """Creates the app, loads the config and binds it to the DB"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(public_bp)

    @app.route("/")
    def backoffice_ui():
        """The Backoffice interface, served from the same origin as the API so
        the session cookie is sent without any CORS handling."""
        return app.send_static_file("index.html")

    return app
