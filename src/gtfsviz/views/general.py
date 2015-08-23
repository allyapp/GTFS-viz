# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

from gtfsviz.views.api import _API_MAPPING


general_blueprint = Blueprint('general', __name__)

@general_blueprint.route('/')
@general_blueprint.route('/index/')
def index():
    """Render index page"""
    return render_template('index.html')


@general_blueprint.route('/api/')
def api_overview():
    """Render API overview page"""
    endpoints = [key for key in _API_MAPPING.iterkeys()]
    return render_template('api.html', endpoints=endpoints)