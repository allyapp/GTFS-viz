# -*- coding: utf-8 -*-

from datetime import datetime

from shapely.geometry import Point
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from gtfsviz.extensions import db


class Stop(db.Model):
    _required_attrs = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    _optional_attrs = ['stop_code', 'stop_desc', 'zone_id', 'stop_url',
                       'location_type', 'parent_station', 'stop_timezone',
                       'wheelchair_boarding']

    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    stop_name = db.Column(db.String, nullable=False)
    stop_lon = db.Column(db.Float, nullable=False)
    stop_lat = db.Column(db.Float, nullable=False)
    geometry = db.Column(Geometry('POINT', srid=4326))
    stop_code = db.Column(db.String)
    stop_desc = db.Column(db.String)
    zone_id = db.Column(db.String)
    stop_url = db.Column(db.String)
    location_type = db.Column(db.Integer)
    stop_timezone = db.Column(db.String)
    parent_station = db.Column(db.String)#, db.ForeignKey('stop.stop_id'))
    #parent_station = db.relationship('Stop', remote_side=[stop_id])
    wheelchair_boarding = db.Column(db.Integer, default=0)
    agency_id = db.Column(db.String, db.ForeignKey('agency.agency_id'))

    @classmethod
    def by_stop_id(cls, id):
        return Stop.query.filter(Stop.stop_id == id).first()

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Stop from the given entity"""
        stop = Stop()
        for attr in stop._required_attrs:
            value = entity.get(attr)
            if attr in ['stop_lat', 'stop_lon']:
                try:
                    value = float(value)
                except ValueError, e:
                    value = 0.0
            setattr(stop, attr, value)

        stop.geometry = from_shape(Point(stop.stop_lon, stop.stop_lat), srid=4326)

        for attr in stop._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['location_type', 'wheelchair_boarding']:
                    try:
                        value = int(value)
                    except ValueError, e:
                        # skipping optional value
                        continue
                setattr(stop, attr, value)
        return stop


class StopTime(db.Model):

    _required_attrs = ['trip_id', 'arrival_time', 'departure_time', 'stop_id',
                       'stop_sequence']
    _optional_attrs = ['stop_headsign', 'pickup_type', 'drop_off_type',
                       'shape_dist_traveled', 'timepoint']

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String, db.ForeignKey('trip.trip_id'))
    trip = db.relationship('Trip', backref=db.backref('stop_times', uselist=True)) # ref to trips
    arrival_time = db.Column(db.String(8), nullable=False, default='')
    departure_time = db.Column(db.String(8), nullable=False, default='')
    stop_id = db.Column(db.String, db.ForeignKey('stop.stop_id'))
    stop = db.relationship('Stop', backref=db.backref('stop_times', uselist=True)) # ref to stops
    stop_sequence = db.Column(db.Integer, nullable=False)
    stop_headsign = db.Column(db.String)
    pickup_type = db.Column(db.Integer)
    drop_off_type = db.Column(db.Integer)
    shape_dist_traveled = db.Column(db.Float)
    timepoint = db.Column(db.Integer)
    agency_id = db.Column(db.String, db.ForeignKey('agency.agency_id'))


    @classmethod
    def by_id(cls, id):
        return StopTime.query.filter(StopTime.id == id).first()

    @classmethod
    def create_from_parser(cls, entity):
        stop_time = StopTime()
        for attr in stop_time._required_attrs:
            value = entity.get(attr)
            if attr in ['stop_sequence']:
                value = int(value)
            setattr(stop_time, attr, value)

        for attr in stop_time._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['pickup_type', 'drop_off_type', 'timepoint']:
                    value = int(value)
                elif attr in ['shape_dist_traveled']:
                    value = float(value)
                setattr(stop_time, attr, value)
        return stop_time