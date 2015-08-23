# -*- coding: utf-8 -*-

"""
This module is responsible for serializing all database objects
into JSON objects.
They will be used by the API endpoints.
"""

from geoalchemy2.elements import WKBElement
from marshmallow import Schema, fields
from sqlalchemy.sql.expression import func

from gtfsviz.extensions import db
import simplejson


class Geom(fields.Field):
    """Field to represent a WKB Geometry"""

    def _serialize(self, value, attr, obj):
        """Converts a WKB Geometry into GeoJSON"""
        if isinstance(value, WKBElement):
            data = db.session.scalar(func.ST_AsGeoJSON(value))
            value = simplejson.loads(data)
        return value

class StopSchema(Schema):
    """Represents a GTFS Stop entity"""
    class Meta:
        json_module = simplejson

    id = fields.Int()
    stop_id = fields.Str()
    stop_name = fields.Str()
    geometry = Geom()
    stop_code = fields.Str(default=None)
    stop_desc = fields.Str(default=None)
    zone_id = fields.Str(default=None)
    stop_url = fields.Str(default=None)
    location_type = fields.Int(default=None)
    stop_timezone = fields.Str(default=None)
    parent_station = fields.Str(default=None)
    wheelchair_boarding = fields.Int()
    #transfer_end = fields.Nested('TransferSchema', many=True, default=None, only=('id',))
    #transfer_start = fields.Nested('TransferSchema', many=True, default=None, only=('id',))
    #stop_times = fields.Nested('StopTimeSchema', many=True, only=('id',))
    agency_id = fields.Str()

class StopTimeSchema(Schema):
    """Represents a GTFS StopTime entity

    It maps the relationships to Trips and Stops directly.
    """

    class Meta:
        json_module = simplejson

    id = fields.Int()
    arrival_time = fields.Str()
    departure_time = fields.Str()
    stop_sequence = fields.Int()
    stop_headsign = fields.Str(default=None)
    pickup_type = fields.Int(default=None)
    drop_off_type = fields.Int(default=None)
    shape_dist_traveled = fields.Float(default=None)
    timepoint = fields.Int(default=None)
    stop_id = fields.Str()
    trip_id = fields.Str()
    stop = fields.Nested('StopSchema', many=False, only='id')
    trip = fields.Nested('TripSchema', exclude=('geometry', ))
    agency_id = fields.Str()


class TransferSchema(Schema):
    """Represents a GTFS Transfer entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    from_stop_id = fields.Str()
    to_stop_id = fields.Str()
    transfer_type = fields.Int()
    min_transfer_type = fields.Int(default=None)


class ShapePointSchema(Schema):
    """Represents a GTFS Shape entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    shape_id = fields.Str()
    shape_pt_lat = fields.Float()
    shape_pt_lon = fields.Float()
    shape_pt_sequence = fields.Int()
    shape_dist_traveled = fields.Float(default=None)
    geometry = Geom()


class ShapeSchema(Schema):
    """Represents a GTFS Shape as Linestring"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    shape_id = fields.Str()
    geometry = Geom()


class FareAttributeSchema(Schema):
    """Represents a GTFS FareAttribute entity

    It maps the relationship to FareRules.
    """

    class Meta:
        json_module = simplejson

    id = fields.Int()
    fare_id = fields.Str()
    price = fields.Float()
    currency_type = fields.Str()
    payment_method = fields.Int()
    transfers = fields.Int()
    transfer_duration = fields.Int(default=None)
    fare_rules = fields.Nested('FareRuleSchema', default=None, many=True, exclude=('fare_attribute',))


class FareRuleSchema(Schema):
    """Represents a GTFS FareRule entity

    It maps the relationship to FareAttributes.
    """

    class Meta:
        json_module = simplejson

    id = fields.Int()
    route_id = fields.Str(default=None)
    origin_id = fields.Str(default=None)
    destination_id = fields.Str(default=None)
    contains_id = fields.Str(default=None)
    fare_id = fields.Str()
    fare_attribute = fields.Nested('FareAttributeSchema')


class RouteSchema(Schema):
    """Represents a GTFS Route entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    route_id = fields.Str()
    route_short_name = fields.Str()
    route_long_name = fields.Str()
    route_type = fields.Str()
    route_desc = fields.Str(default=None)
    route_url = fields.Str(default=None)
    route_color = fields.Str()
    route_text_color = fields.Str()
    agency_id = fields.Str()
    geometry = Geom()


class TripSchema(Schema):
    """Represents a GTFS Trip entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    trip_id = fields.Str()
    trip_headsign = fields.Str(default=None)
    trip_short_name = fields.Str(default=None)
    direction_id = fields.Int(default=None)
    block_id = fields.Str(default=None)
    bikes_allowed = fields.Int()
    route_id = fields.Str()
    shape_id = fields.Str(default=None)
    service_id = fields.Str()
    service_date_id = fields.Str(default=None)
    wheelchair_accessible = fields.Int()
    agency_id = fields.Str()
    geometry = Geom()


class FrequencySchema(Schema):
    """Represents a GTFS Frequency entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    start_time = fields.Str()
    end_time = fields.Str()
    headway_secs = fields.Int()
    exact_times = fields.Int()
    trip_id = fields.Str()

class FeedInfoSchema(Schema):
    """Represents a GTFS FeedInfo entity

    It maps the relationship to Agencies.
    """
    class Meta:
        json_module = simplejson

    id = fields.Int()
    feed_publisher_name = fields.Str()
    feed_publisher_url = fields.Str()
    feed_lang = fields.Str()
    feed_start_date = fields.Date(default=None)
    feed_end_date = fields.Date(default=None)
    feed_version = fields.Str(default=None)
    agencies = fields.Nested('AgencySchema', many=True, exclude=('feed_info',))

class ServiceSchema(Schema):
    """Represents a GTFS Calendar entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    service_id = fields.Str()
    monday = fields.Bool()
    tuesday = fields.Bool()
    wednesday = fields.Bool()
    thursday = fields.Bool()
    friday = fields.Bool()
    saturday = fields.Bool()
    sunday = fields.Bool()
    start_date = fields.Date()
    end_date = fields.Date()
    #trips = fields.Nested(TripSchema, many=True, exclude=('service', 'agency', 'stop_times', 'route'))

class ServiceDateSchema(Schema):
    """Represents a GTFS CalendarDates entity"""

    class Meta:
        json_module = simplejson

    id = fields.Int()
    service_id = fields.Str()
    date = fields.Date()
    exception_type = fields.Int()
    #trips = fields.Nested(TripSchema, many=True, exclude=('service_date', 'agency', 'stop_time', 'route'))


class AgencySchema(Schema):
    """Represents a GTFS Agency entity

    It maps the relationship to FeedInfo.
    """
    class Meta:
        json_module = simplejson

    id = fields.Int()
    agency_id = fields.Str()
    agency_name = fields.Str()
    agency_url = fields.Str()
    agency_timezone = fields.Str()
    agency_lang = fields.Str(default=None)
    agency_phone = fields.Str(default=None)
    agency_fare_url = fields.Str(default=None)
    geometry = Geom()
    #routes = fields.Nested(RouteSchema, many=True, exclude=('agency','trips','fare_rules'))
    #trips = fields.Nested(TripSchema, many=True, exclude=('agency', 'stop_times', 'service', 'service_date', 'frequencies'))
    #stops = fields.Nested(StopSchema, many=True, exclude=('agency', 'stop_times'))
    feed_info = fields.Nested(FeedInfoSchema, default=None, exclude=('agencies',))


agency_schema = AgencySchema()
fare_attribute_schema = FareAttributeSchema()
fare_rule_schema = FareRuleSchema()
feed_info_schema = FeedInfoSchema()
frequency_schema = FrequencySchema()
route_schema = RouteSchema()
service_schema = ServiceSchema()
service_date_schema = ServiceDateSchema()
shape_point_schema = ShapePointSchema()
shape_schema = ShapeSchema()
stop_schema = StopSchema()
stop_time_schema = StopTimeSchema()
transfer_schema = TransferSchema()
trip_schema = TripSchema()

# serializer functions, used by flask-restless
def agency_serializer(instance):
    return agency_schema.dump(instance).data

def fare_attribute_serializer(instance):
    return fare_attribute_schema.dump(instance).data

def fare_rule_serializer(instance):
    return fare_rule_schema.dump(instance).data

def feed_info_serializer(instance):
    return feed_info_schema.dump(instance).data

def frequency_serializer(instance):
    return frequency_schema.dump(instance).data

def route_serializer(instance):
    return route_schema.dump(instance).data

def service_serializer(instance):
    return service_schema.dump(instance).data

def service_date_serializer(instance):
    return service_date_schema.dump(instance).data

def shape_point_serializer(instance):
    return shape_point_schema.dump(instance).data

def shape_serializer(instance):
    return shape_schema.dump(instance).data

def stop_serializer(instance):
    return stop_schema.dump(instance).data

def stop_time_serializer(instance):
    return stop_time_schema.dump(instance).data

def transfer_serializer(instance):
    return transfer_schema.dump(instance).data

def trip_serializer(instance):
    return trip_schema.dump(instance).data

