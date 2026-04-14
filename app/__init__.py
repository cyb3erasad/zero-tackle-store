import os
from flask import Flask
from app.config import config_map
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name=None):
    """
    App factory function.
    Creates and configures the Flask application.
    All blueprints and extensions are registered here.
    """

    app = Flask(__name__)

    # ------------------------------------------------------------------ #
    # Load config
    # ------------------------------------------------------------------ #
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app.config.from_object(config_map[config_name])

    # ------------------------------------------------------------------ #
    # Initialize extensions with the app
    # ------------------------------------------------------------------ #
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ------------------------------------------------------------------ #
    # Import models so Flask-Migrate can detect them
    # ------------------------------------------------------------------ #
    from app import models  # noqa: F401

    # ------------------------------------------------------------------ #
    # Register blueprints
    # ------------------------------------------------------------------ #
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/products')

    from app.cart import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    from app.orders import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders')

    from app.reviews import reviews_bp
    app.register_blueprint(reviews_bp, url_prefix='/reviews')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app