# -*- coding: utf-8 -*-

from pathlib import Path

BASEDIR = Path(__file__).absolute().parent

class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://gtfs:gtfs@127.0.0.1:5432/gtfs'
    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_ECHO = False



