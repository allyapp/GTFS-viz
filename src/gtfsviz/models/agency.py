# -*- coding: utf-8 -*-

from datetime import datetime

from shapely.geometry import Polygon, asShape
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from gtfsviz.extensions import db


class Agency(db.Model):
    """Represents a Agency entity from a GTFS feed."""

    _required_attrs = ['agency_name', 'agency_url', 'agency_timezone']
    _optional_attrs = ['agency_id', 'agency_lang', 'agency_phone',
                       'agency_fare_url']

    id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    agency_name = db.Column(db.String, nullable=False)
    agency_url = db.Column(db.String, nullable=False)
    agency_timezone = db.Column(db.String(50), nullable=False)
    agency_lang = db.Column(db.String(10))
    agency_phone = db.Column(db.String(50))
    agency_fare_url = db.Column(db.String)
    routes = db.relationship('Route', uselist=True, backref='agency')
    trips = db.relationship('Trip', uselist=True, backref='agency')
    stop_times = db.relationship('StopTime', uselist=True, backref='agency')
    stops = db.relationship('Stop', uselist=True, backref='agency')

    feed_info_id = db.Column(db.String, db.ForeignKey('feed_info.feed_publisher_name'))
    feed_info = db.relationship('FeedInfo', backref='agencies')
    geometry = db.Column(Geometry('POLYGON', srid=4326))

    @classmethod
    def by_agency_id(cls, id):
        """Get a Agency by ID"""
        return Agency.query.filter(Agency.agency_id == id).first()


    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Agency from the given entity"""
        agency = Agency()
        for attr in agency._required_attrs:
            value = entity.get(attr)
            setattr(agency, attr, value)

        for attr in agency._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['feed_start_date', 'feed_end_date']:
                    try:
                        value = datetime.strptime(value, '%Y%m%d')
                    except ValueError, e:
                        # skipping optional attr
                        continue
                setattr(agency, attr, value)

        # build the geometry
        agency.geometry = from_shape(asShape(entity.geometry()), srid=4326)
        return agency


