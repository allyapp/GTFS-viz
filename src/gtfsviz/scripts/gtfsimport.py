# -*- coding: utf-8 -*-

import os
import sys


from mzgtfs.feed import Feed


from progress.bar import Bar

from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from pathlib import Path

from shapely.geometry import LineString

from gtfsviz import models
from gtfsviz.extensions import db
from gtfsviz.scripts.utils import create_temporary_zipfile


class ImportError(Exception):
    pass

def _parse_feed(feed_path):
    """Parse the GTFS feed

    If the feed is a directory, create a tmp zip file first.
    mzgtfs.feed can't read directories.
    """
    try:
        path = Path(feed_path)
    except TypeError, e:
        return

    file_path = None

    if path.exists() and path.suffix == '.zip':
        feed = Feed(feed_path)
    elif path.exists() and path.is_dir():
        # the zipfile is not deleted, not all data will be completly
        # loaded when calling feed.preload()
        handle, file_path = create_temporary_zipfile(path)
        feed = Feed(file_path)
    else:
        raise ImportError('The submitted path is not a valid GTFS feed')

    try:
        feed.preload()
    except KeyError, e:
        raise ImportError(e)

    return feed, file_path


def _create_linestrings(shapes):
    """create LineStrings for all Shapes.

    First: collect all points belonging to the same shape.
    Second: sort them by shape_pt_sequence.
    Third: create the geometry with shapely and geoalchemy2.
    """

    bar = Bar('Creating LineStrings from shapes', max=len(shapes)+2, suffix='%(percent)d%%')
    # filter shapes by id:
    bar.next()
    linestrings = {}
    for s in shapes:
        elem_list = linestrings.get(s.shape_id, [])
        elem_list.append(s)
        linestrings[s.shape_id] = elem_list

    objects = []
    for key, shape_points  in linestrings.iteritems():
        obj = models.Shape()
        obj.shape_id = key
        obj.points = shape_points
        sorted_points = sorted(shape_points, key=lambda x: x.shape_pt_sequence)
        point_array = [(x.shape_pt_lon, x.shape_pt_lat) for x in sorted_points]
        linestring = LineString(point_array)
        obj.geometry = from_shape(linestring, srid=4326)
        db.session.add(obj)
        bar.next(len(shape_points))

    db.session.commit()
    bar.next()
    bar.finish()
    return objects

def _build_trip_geom(trips):
    """Create geometries for all trips."""
    for trip in trips:
        trip.build_geometry()
        db.session.add(trip)
    db.session.commit()

def _build_route_geoms(routes):
    """Create geometries for all routes."""
    for route in routes:
        route.build_geometry()
        db.session.add(route)
    db.session.commit()

def _create_db_objects(entities, create_fn, progress_label, relationship=None):
    """Call the classmethod of each model to create a db object for the entity"""
    bar = Bar(progress_label, max=len(entities)+1, suffix='%(percent)d%%')
    objects = []
    for e in entities:
        obj = create_fn(e)
        db.session.add(obj)
        if relationship is not None:
            attr_name, attr_value = relationship
            setattr(obj, attr_name, attr_value)
        objects.append(obj)
        bar.next()
    try:
        db.session.commit()
    except Exception, e:
        bar.finish()
        raise ImportError(e)
    else:
        bar.next()
        bar.finish()
        return objects

CREATE_FUNCTIONS = {
    'feed_info': (models.FeedInfo.create_from_parser,),
    'calendar_dates': (models.ServiceDate.create_from_parser,),
    'shapes': (models.ShapePoint.create_from_parser, _create_linestrings),
    'fare_rules': (models.FareRule.create_from_parser,),
    'transfers': (models.Transfer.create_from_parser,),
    'frequencies': (models.Frequency.create_from_parser,),
    'agencies': (models.Agency.create_from_parser,),
    'routes': (models.Route.create_from_parser,),
    'trips': (models.Trip.create_from_parser,),
    'stops': (models.Stop.create_from_parser,),
    'stop_times': (models.StopTime.create_from_parser,),
    'calendar': (models.Service.create_from_parser,),
    'fare_attributes': (models.FareAttribute.create_from_parser,)
}

def _parse_optional_files(feed, tablename):
    """Read an optional file from the feed and populate the db."""
    try:
        entities = feed.read(tablename)
    except KeyError, e:
        print 'Skipping file %s (Not found)' % tablename
    else:
        if not entities:
            print 'Skipping %s (The file was not found or its contents were empty)' % tablename
            return []

        try:
            obj_fn, additional_fn = CREATE_FUNCTIONS[tablename]
        except ValueError, e:
            obj_fn = CREATE_FUNCTIONS[tablename][0]
            additional_fn = None

        # After importing Shapes, populate the ShapePoint table
        # and create LineStrings for the Shapes table.
        objects = _create_db_objects(entities, obj_fn, 'Importing %s' % tablename)
        if additional_fn is not None:
            additional_objects = additional_fn(objects)
            objects = objects + additional_objects

        return objects

def _populate_db(feed):
    """Start populating the database with all entities found in the feed."""

    feed_info = _parse_optional_files(feed, 'feed_info')
    services = _create_db_objects(feed.serviceperiods(),
                                  CREATE_FUNCTIONS['calendar'][0],
                                  'Importing calendar')
    service_dates = _parse_optional_files(feed, 'calendar_dates')
    shapes = _parse_optional_files(feed, 'shapes')

    # create a relationship to all agencies, if a feed info is available
    if feed_info:
        agencies = _create_db_objects(feed.agencies(),
                                      CREATE_FUNCTIONS['agencies'][0],
                                      'Importing agencies',
                                      relationship=('feed_info', feed_info[0]))
    else:
        agencies = _create_db_objects(feed.agencies(),
                                      CREATE_FUNCTIONS['agencies'][0],
                                      'Importing agencies')

    # store all trips and routes in memory to build the geometry
    # attribute for them
    all_trips = []
    all_routes = []
    for db_entity, agency in zip(agencies, feed.agencies()):
        label = 'Importing %s (Agency: %s)'
        stops = _create_db_objects(agency.stops(),
                                   CREATE_FUNCTIONS['stops'][0],
                                   label % ('stops', agency.name()),
                                   relationship=('agency', db_entity))
        routes = _create_db_objects(agency.routes(),
                                   CREATE_FUNCTIONS['routes'][0],
                                   label % ('routes', agency.name()),
                                   relationship=('agency', db_entity))
        trips = _create_db_objects(agency.trips(),
                                   CREATE_FUNCTIONS['trips'][0],
                                   label % ('trips', agency.name()),
                                   relationship=('agency', db_entity))
        all_trips.extend(trips)
        all_routes.extend(routes)
        stop_times = _create_db_objects(agency.stop_times(),
                                        CREATE_FUNCTIONS['stop_times'][0],
                                        label % ('stop_times', agency.name()),
                                        relationship=('agency',db_entity))

    _build_trip_geom(all_trips)
    _build_route_geoms(all_routes)

    fare_attributes = _parse_optional_files(feed, 'fare_attributes')
    fare_rules = _parse_optional_files(feed, 'fare_rules')
    transfers = _parse_optional_files(feed, 'transfers')
    frequencies = _parse_optional_files(feed, 'frequencies')


def import_gtfs_feed(feed_path):
    """Import the GTFS feed to a postgis db.

    Note: The database should be empty to avoid import errors caused
    by duplicate keys by different GTFS feeds.
    """

    print 'Parsing GTFS feed...'
    tmp_file = None
    try:
        feed, tmp_file = _parse_feed(feed_path)
    except ImportError, e:
        if tmp_file is not None:
            os.unlink(tmp_file)
        print str(e)
        sys.exit(1)

    try:
        _populate_db(feed)
    except ImportError, e:
        print str(e)
        print 'Aborting import...'
    else:
        print 'Done.'

    if tmp_file is not None:
        os.unlink(tmp_file)
