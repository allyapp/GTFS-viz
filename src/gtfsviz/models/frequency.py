# -*- coding: utf-8 -*-

from gtfsviz.extensions import db

class Frequency(db.Model):
    """Represents a Frequency entity from a GTFS feed."""

    _required_attrs = ['trip_id', 'start_time', 'end_time', 'headway_secs']
    _optional_attrs = ['exact_times']

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String, db.ForeignKey('trip.trip_id'), nullable=False)
    start_time = db.Column(db.String(8), nullable=False)
    end_time = db.Column(db.String(8), nullable=False)
    headway_secs = db.Column(db.Integer, nullable=False)
    exact_times = db.Column(db.Integer, default=0)
    trip = db.relationship('Trip', backref='frequencies', uselist=False)


    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Frequency from the given entity"""

        freq = Frequency()
        for attr in freq._required_attrs:
            value = entity.get(attr)
            if attr in ['headway_secs']:
                try:
                    value = int(value)
                except ValueError, e:
                    value = -1
            setattr(freq, attr, value)

        for attr in freq._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['exact_times']:
                    try:
                        value = int(value)
                    except ValueError, e:
                        # skipping optional attr
                        continue
                setattr(freq, attr, value)

        return freq