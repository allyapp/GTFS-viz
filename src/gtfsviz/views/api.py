# -*- coding: utf-8 -*-

from gtfsviz.models import (
    Agency, Service, ServiceDate, FareAttribute, FareRule, FeedInfo, Frequency,
    Route, Shape, ShapePoint, Stop, StopTime, Transfer, Trip
)
from gtfsviz.models.schemas import (
     agency_serializer, fare_attribute_serializer, fare_rule_serializer,
     feed_info_serializer, frequency_serializer, route_serializer,
     service_serializer, service_date_serializer, shape_point_serializer,
     shape_serializer, stop_serializer, stop_time_serializer,
     transfer_serializer, trip_serializer
)
from gtfsviz.extensions import api_manager


_API_MAPPING = {
    'Agency': (Agency, agency_serializer),
    'Service': (Service, service_serializer),
    'ServiceDate': (ServiceDate, service_date_serializer),
    'FareAttribute': (FareAttribute, fare_attribute_serializer),
    'FareRule': (FareRule, fare_rule_serializer),
    'FeedInfo': (FeedInfo, feed_info_serializer),
    'Frequency': (Frequency, frequency_serializer),
    'Route': (Route, route_serializer),
    'Shape': (Shape, shape_serializer),
    'ShapePoint': (ShapePoint, shape_point_serializer),
    'Stop': (Stop, stop_serializer),
    'StopTime': (StopTime, stop_time_serializer),
    'Transfer': (Transfer, transfer_serializer),
    'Trip': (Trip, trip_serializer)
}


def create_blueprints(app):
    """Create a endpoint for each db.model defined in _API_MAPPING"""
    blueprints = []
    for key, values in _API_MAPPING.iteritems():
        klass, serializer = values
        include_columns = klass._required_attrs + klass._optional_attrs + ['id']
        blueprint = api_manager.create_api_blueprint(klass, app=app,
                                                     serializer=serializer,
                                                     results_per_page=50,
                                                     max_results_per_page=500,
                                                     include_columns=include_columns,
                                                     primary_key='id')

        blueprints.append(blueprint)

    return blueprints