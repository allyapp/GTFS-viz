# -*- coding: utf-8 -*-

from geoalchemy2 import Geometry

from gtfsviz.extensions import db
from gtfsviz.models.calendar import Service, ServiceDate


class Trip(db.Model):
    """Represents a trip entity from a GTFS feed."""

    _required_attrs = ['trip_id', 'route_id', 'service_id']
    _optional_attrs = ['trip_headsign', 'trip_short_name', 'direction_id',
                       'block_id', 'shape_id', 'wheelchair_accessible',
                       'bikes_allowed']

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String, db.ForeignKey('route.route_id'), nullable=False)
    trip_id = db.Column(db.String, nullable=False, primary_key=True, unique=True)
    trip_headsign = db.Column(db.String)
    trip_short_name = db.Column(db.String)
    direction_id = db.Column(db.Integer)
    block_id = db.Column(db.String)
    geometry = db.Column(Geometry('LINESTRING', srid=4326))
    shape_id = db.Column(db.String, db.ForeignKey('shape.shape_id'))
    service_id = db.Column(db.String, db.ForeignKey('service.service_id'))
    service = db.relationship('Service', uselist=False, backref='trips')
    service_date_id = db.Column(db.String)
    wheelchair_accessible = db.Column(db.Integer, default=0)
    bikes_allowed = db.Column(db.Integer, default=0)
    agency_id = db.Column(db.String, db.ForeignKey('agency.agency_id'))

    @classmethod
    def by_trip_id(cls, id):
        """Get a Trip by id"""
        return Trip.query.filter(Trip.trip_id == id).first()

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Trip from the given entity"""
        trip = Trip()
        for attr in trip._required_attrs:
            value = entity.get(attr)
            setattr(trip, attr, value)

        for attr in trip._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['direction_id', 'wheelchair_accessible', 'bikes_allowed']:
                    try:
                        value = int(value)
                    except ValueError, e:
                        value = -1

                # since a calender.txt or/and calender_dates.txt can be used
                # we need to insert the reference manually and not via settattr
                elif attr in ['service_id']:
                    service_date = ServiceDate.by_service_id(value)
                    if service_date:
                        trip.service_date_id = value
                    service = Service.by_service_id(value)
                    if service:
                        trip.service_id = value
                    continue
                setattr(trip, attr, value)
        return trip

    def build_geometry(self):
        """Copy the geometry from the connected shape."""
        if self.shape:
            self.geometry = self.shape.geometry