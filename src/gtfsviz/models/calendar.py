# -*- coding: utf-8 -*-

from datetime import datetime

from gtfsviz.extensions import db


class Service(db.Model):
    """Represents a Calendar entity from a GTFS feed."""


    _required_attrs = ['service_id', 'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday', 'start_date',
                       'end_date']
    _optional_attrs = []

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    monday = db.Column(db.Boolean, nullable=False)
    tuesday = db.Column(db.Boolean, nullable=False)
    wednesday = db.Column(db.Boolean, nullable=False)
    thursday = db.Column(db.Boolean, nullable=False)
    friday = db.Column(db.Boolean, nullable=False)
    saturday = db.Column(db.Boolean, nullable=False)
    sunday = db.Column(db.Boolean, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    @classmethod
    def by_service_id(cls, id):
        """Get a Service by id"""
        return Service.query.filter(Service.service_id == id).first()

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Service from the given entity"""

        service = Service()
        for attr in service._required_attrs:
            value = entity.get(attr)
            if attr in ['start_date', 'end_date']:
                try:
                    value = datetime.strptime(value, '%Y%m%d')
                except ValueError, e:
                    # which date to use, when an error occurs?
                    value = 0
            elif attr in ['service_id']:
                # pass the value to setattr as is.
                pass
            else:
                value = bool(int(value))
            setattr(service, attr, value)

        return service

class ServiceDate(db.Model):
    """Represents a CalendarDate entity from a GTFS feed."""

    __table_args__ = (
        db.UniqueConstraint('service_id', 'date'),
    )

    _required_attrs = ['service_id', 'date', 'exception_type']
    _optional_attrs = []

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    exception_type = db.Column(db.Integer, nullable=False)

    @classmethod
    def by_service_id(cls, id):
        """Get a ServiceDate by ID"""
        return ServiceDate.query.filter(ServiceDate.service_id == id).first()

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new ServiceDate from the given entity"""

        service_date = ServiceDate()
        for attr in service_date._required_attrs:
            value = entity.get(attr)
            if attr in ['date']:
                try:
                    value = datetime.strptime(value, '%Y%m%d')
                except ValueError, e:
                    # which date to use, when an error occurs?
                    value = 0
            elif attr in ['exception_type']:
                try:
                    value = int(value)
                except ValueError, e:
                    value = -1
            setattr(service_date, attr, value)

        return service_date