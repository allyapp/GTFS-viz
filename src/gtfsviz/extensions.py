# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.restless import APIManager
api_manager = APIManager()
