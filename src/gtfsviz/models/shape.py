# -*- coding: utf-8 -*-

from datetime import datetime

from shapely.geometry import Point
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from gtfsviz.extensions import db



class ShapePoint(db.Model):
    """Represents a ShapePoint entity from a GTFS feed."""

    _required_attrs = ['shape_id', 'shape_pt_lat', 'shape_pt_lon',
                       'shape_pt_sequence']
    _optional_attrs = ['shape_dist_traveled']

    id = db.Column(db.Integer, primary_key=True)
    shape_id = db.Column(db.String, nullable=False, primary_key=True, index=True)
    shape_pt_lat = db.Column(db.Float, nullable=False)
    shape_pt_lon = db.Column(db.Float, nullable=False)
    shape_pt_sequence = db.Column(db.Integer)
    shape_dist_traveled = db.Column(db.Float)
    geometry = db.Column(Geometry('POINT', srid=4326))
    parent_id = db.Column(db.String, db.ForeignKey('shape.shape_id'))

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new ShapePoint from the given entity"""

        shape_point = ShapePoint()
        for attr in shape_point._required_attrs:
            value = entity.get(attr)
            if attr in ['shape_pt_lat', 'shape_pt_lon']:
                try:
                    value = float(value)
                except ValueError, e:
                    value = 0.0
            elif attr in ['shape_pt_sequence']:
                try:
                    value = int(value)
                except ValueError, e:
                    value = 0
            setattr(shape_point, attr, value)

        # build the geometry with shapely
        shape_point.Geometry = from_shape(Point(shape_point.shape_pt_lon,
                                                shape_point.shape_pt_lat),
                                          srid=4326)

        for attr in shape_point._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['shape_dist_traveled']:
                    try:
                        value = int(value)
                    except ValueError, e:
                        # skipping optional attr
                        continue
                setattr(shape_point, attr, value)

        return shape_point


class Shape(db.Model):
    """Represents a Shape with a LineString geometry.

    It is created by a list of ShapePoints.
    """

    _required_attrs = ['shape_id']
    _optional_attrs = []

    id = db.Column(db.Integer, primary_key=True)
    geometry = db.Column(Geometry('LINESTRING', srid=4326))
    shape_id = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    points = db.relationship('ShapePoint', backref='shape', uselist=True)
    trips = db.relationship('Trip', backref='shape', uselist=True)

    @classmethod
    def by_shape_id(cls, id):
        """Get a Shape by ID"""
        return Shape.query.filter(Shape.shape_id==id).first()
