# -*- coding: utf-8 -*-
from gtfsviz.extensions import db


class Transfer(db.Model):
    """Represents a transfer entity from a GTFS feed."""

    _required_attrs = ['from_stop_id', 'to_stop_id', 'transfer_type']
    _optional_attrs = ['min_transfer_time']

    id = db.Column(db.Integer, primary_key=True)
    from_stop_id = db.Column(db.String, db.ForeignKey('stop.stop_id'), nullable=False)
    to_stop_id = db.Column(db.String, db.ForeignKey('stop.stop_id'), nullable=False)
    stop_to = db.relationship('Stop', foreign_keys=[to_stop_id], backref='transfer_end', uselist=False)
    stop_from = db.relationship('Stop', foreign_keys=[from_stop_id], backref='transfer_start', uselist=False)
    transfer_type = db.Column(db.Integer, nullable=False, default=0)
    min_transfer_time = db.Column(db.Integer)

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new Transfer from the given entity"""
        transfer = Transfer()
        for attr in transfer._required_attrs:
            value = entity.get(attr)
            if attr in ['transfer_type']:
                try:
                    value = int(value)
                except ValueError, e:
                    value = -1
            setattr(transfer, attr, value)

        for attr in transfer._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['min_transfer_time']:
                    try:
                        value = int(value)
                    except ValueError, e:
                        # skipping optional value
                        continue
                setattr(transfer, attr, value)

        return transfer