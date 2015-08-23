# -*- coding: utf-8 -*-

from datetime import datetime

from shapely.ops import cascaded_union
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.sql.expression import func

from gtfsviz.extensions import db


class Route(db.Model):
    """Represents a route entity from a GTFS feed."""

    _required_attrs = ['route_id', 'route_short_name', 'route_long_name',
                       'route_type']
    _optional_attrs = ['agency_id', 'route_desc', 'route_url', 'route_color',
                       'route_text_color']

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String, nullable=False, primary_key=True, unique=True)
    route_short_name = db.Column(db.String, nullable=False)
    route_long_name = db.Column(db.String, nullable=False)
    route_type = db.Column(db.String, nullable=False)
    route_desc = db.Column(db.String)
    route_url = db.Column(db.String)
    route_color = db.Column(db.String(6), default='FFFFFF')
    route_text_color = db.Column(db.String(6), default='000000')
    agency_id = db.Column(db.String, db.ForeignKey('agency.agency_id'))
    trips = db.relationship('Trip', uselist=True)
    geometry = db.Column(Geometry('MULTILINESTRING', srid=4326))

    @classmethod
    def by_route_id(cls, id):
        """Get a Route by id"""
        return Route.query.filter(Route.route_id == id).first()

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Route from the given entity"""
        route = Route()
        for attr in route._required_attrs:
            value = entity.get(attr)
            if attr in ['stop_sequence']:
                try:
                    value = int(value)
                except ValueError, e:
                    value = -1
            setattr(route, attr, value)

        for attr in route._optional_attrs:
            value = entity.get(attr)
            if value:
                setattr(route, attr, value)
        return route

    def build_geometry(self):
        """Copy the geometry from the trips and merge them"""
        geoms = [to_shape(t.geometry) for t in self.trips]
        if geoms:
            geom = cascaded_union(geoms)
            geom = from_shape(geom, srid=4326)
            self.geometry = db.session.scalar(func.ST_MULTI(func.ST_SimplifyPreserveTopology(geom, 0.00005)))