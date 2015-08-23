# -*- coding: utf-8 -*-
from datetime import datetime

from gtfsviz.extensions import db


class FeedInfo(db.Model):
    """Represents a FeedInfo entity from a GTFS feed."""

    _required_attrs = ['feed_publisher_name', 'feed_publisher_url', 'feed_lang']
    _optional_attrs = ['feed_start_date', 'feed_end_date', 'feed_version']

    id = db.Column(db.Integer, primary_key=True)
    feed_publisher_name = db.Column(db.String, nullable=False, index=True, unique=True)
    feed_publisher_url = db.Column(db.String, nullable=False)
    feed_lang = db.Column(db.String, nullable=False)
    feed_start_date = db.Column(db.Date)
    feed_end_date = db.Column(db.Date)
    feed_version = db.Column(db.String)

    @classmethod
    def create_from_parser(cls, entity):
        """Create a new FeedInfo from the given entity"""
        feed_info = FeedInfo()
        for attr in feed_info._required_attrs:
            value = entity.get(attr)
            setattr(feed_info, attr, value)

        for attr in feed_info._optional_attrs:
            value = entity.get(attr)
            if value:
                if attr in ['feed_start_date', 'feed_end_date']:
                    try:
                        value = datetime.strptime(value, '%Y%m%d')
                    except ValueError,e:
                        # skipping optional attr
                        continue
                setattr(feed_info, attr, value)

        return feed_info

