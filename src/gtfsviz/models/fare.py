# -*- coding: utf-8 -*-

from gtfsviz.extensions import db

class FareAttribute(db.Model):
    """Represents a FareAttribute entity from a GTFS feed."""

    _required_attrs = ['fare_id', 'price', 'currency_type', 'payment_method',
                       'transfers']
    _optional_attrs = ['transfer_duration']

    id = db.Column(db.Integer, primary_key=True)
    fare_id = db.Column(db.String, nullable=False, unique=True, index=True, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    currency_type = db.Column(db.String, nullable=False)
    payment_method = db.Column(db.Integer, nullable=False)
    transfers = db.Column(db.Integer)
    transfer_duration = db.Column(db.Integer)

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new FareAttribute from the given entity"""

        fare_attribute = FareAttribute()
        for attr in fare_attribute._required_attrs:
            value = entity.get(attr)
            if attr in ['price']:
                try:
                    value = float(value)
                except ValueError, e:
                    value = -1
            elif attr in ['payment_method', 'transfers']:
                try:
                    value = int(value)
                except ValueError, e:
                    value = -1
            setattr(fare_attribute, attr, value)

        for attr in fare_attribute._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['transfer_duration']:
                    try:
                        value = int(value)
                    except ValueError, e:
                        # skipping optional attr
                        continue
                setattr(fare_attribute, attr, value)

        return fare_attribute

class FareRule(db.Model):
    """Represents a FareRule entity from a GTFS feed."""

    _required_attrs = ['fare_id']
    _optional_attrs = ['route_id', 'origin_id', 'destination_id', 'contains_id']

    id = db.Column(db.Integer, primary_key=True)
    fare_id = db.Column(db.String, db.ForeignKey('fare_attribute.fare_id'), nullable=False)
    fare_attribute = db.relationship('FareAttribute', backref='fare_rules', uselist=False)
    route_id = db.Column(db.String, nullable=True)
    origin_id = db.Column(db.String, nullable=True)
    destination_id = db.Column(db.String, nullable=True)
    contains_id = db.Column(db.String, nullable=True)

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new FareRule from the given entity"""

        fare_rule = FareRule()
        for attr in fare_rule._required_attrs:
            value = entity.get(attr)
            setattr(fare_rule, attr, value)

        for attr in fare_rule._optional_attrs:
            value = entity.get(attr)
            if value:
                setattr(fare_rule, attr, value)

        return fare_rule