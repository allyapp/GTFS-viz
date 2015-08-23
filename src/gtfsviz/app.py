# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, jsonify

from shapely import speedups

from gtfsviz.extensions import db, api_manager

if speedups.available:
    speedups.enable()
else:
    print 'shapely speedups not available'

__all__ = ['create_app']


def create_app(config=None, app_name='gtfsviz'):
    """Creates the server and loads the config for this project."""
    app = Flask(app_name,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

    if config:
        app.config.from_object(config)

    configure_error_handlers(app)

    register_extensions(app)
    register_blueprints(app)

    return app


def register_blueprints(app):
    """Each blueprint is a view endpoint which needs to be registered in the app."""

    from gtfsviz.views.api import create_blueprints
    from gtfsviz.views.general import general_blueprint
    for bp in create_blueprints(app):
        app.register_blueprint(bp)
    app.register_blueprint(general_blueprint)


def register_extensions(app):
    """Add extensions to the flask app."""
    db.init_app(app)
    api_manager.init_app(app, flask_sqlalchemy_db=db)


def configure_error_handlers(app):
    """HTTP error pages definitions."""

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template('errors/forbidden_page.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/page_not_found.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template('errors/method_not_allowed.html'), 405

    @app.errorhandler(500)
    def server_error_page(error):
            return render_template('errors/server_error.html'), 500

    # @app.errorhandler(Exception)
    # def others(error):
    #     return jsonify(error=str(error)), 400
