# -*- coding: utf-8 -*-

import click

from gtfsviz.app import create_app
from gtfsviz.config import BaseConfig, ProductionConfig
from gtfsviz.extensions import db
from gtfsviz.scripts.gtfsimport import import_gtfs_feed

@click.group()
def server():
    pass

@server.command()
def debug():
    """Run locally in debug mode."""
    app = create_app(BaseConfig)
    app.run(host='127.0.0.1', debug=True)

@server.command()
def runserver():
    """Run locally"""
    app = create_app(ProductionConfig)
    app.run(host='127.0.0.1')

@server.command()
@click.option('--path', help='path/to/dir or path/to/sample-feed.zip')
def feed(path):
    app = create_app(ProductionConfig)
    with app.app_context() as ctx:
        import_gtfs_feed(path)


@click.group()
def database():
    pass

@database.command()
def create_db():
    """Command on database"""
    app = create_app(ProductionConfig)
    with app.app_context() as ctx:
        db.drop_all()
        db.create_all()

cli = click.CommandCollection(sources=[server, database])

if __name__ == "__main__":
    cli()
