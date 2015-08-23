var agencies = [],
    routes = [],
    trips = [],
    stops = [];

$(document).ready(function(){
    var map = L.map('map').setView([19.44374, -99.14054], 12);
    var basemap = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: 'quiqua.m5708fgk',
        accessToken: 'pk.eyJ1IjoicXVpcXVhIiwiYSI6Ik0ySHI4X3cifQ.VugiUOPOVSD2_E_mgN-2Jw',
    }).addTo(map);


    var geojsonMarkerOptions = {
        radius: 2,
        fillColor: "#ff7800",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    };

    var agencyFeatures = L.featureGroup().addTo(map);
    var routeFeatures = L.featureGroup().addTo(map);
    var tripFeatures = L.featureGroup().addTo(map);
    var stopFeatures = L.featureGroup().addTo(map);
    var selectedFeature = L.featureGroup().addTo(map);

    var baseMaps = {
        "Basemap": basemap
    };

    var overlayMaps = {
        "Agencies": agencyFeatures,
        "Routes": routeFeatures,
        "Trips": tripFeatures,
        "Stops": stopFeatures,
        "Selected": selectedFeature
    };

    L.control.layers(baseMaps, overlayMaps, {collapsed: false}).addTo(map);

    var qualitativeColors = [
        ['#a6cee3', false],
        ['#1f78b4', false],
        ['#b2df8a', false],
        ['#33a02c', false],
        ['#fb9a99', false],
        ['#e31a1c', false],
        ['#fdbf6f', false],
        ['#ff7f00', false],
        ['#cab2d6', false],
        ['#6a3d9a', false],
        ['#ffff99', false]
    ];

    /* ensure any open panels are closed before showing selected */
    $('#accordion').on('show.bs.collapse', function () {
        $('#accordion .in').collapse('hide');
    });

    function toGeoJson(elem, options){
        var geojson = {type:'Feature', properties: {}, geometry: {}}
            geojson.geometry = elem.geometry

            for (var i in elem){
                if (i !== 'geometry'){
                    geojson.properties[i] = elem[i]
                }
            }
            return geojson
    }

    function addRouteToMap(route){
        route.route_color = '#' + route.route_color;
        var geojson = toGeoJson(route)
        var feature = L.geoJson(geojson, {
                style: function(feature){
                    return {color: feature.properties.route_color}
                },
                onEachFeature: function (feature, layer) {
                    var p = feature.properties;
                    var contents = '<h5>Route: '+p.route_id+' ' +p.route_long_name+
                                   '</h5>';
                    layer.bindPopup(contents);
                },
            });

        feature.on('click', function(){

        });
        routeFeatures.addLayer(feature);
        return feature._leaflet_id;

    }

    function addAgencyToMap(agency){
        var geojson = toGeoJson(agency)
        var feature = L.geoJson(geojson, {
                style: function(feature){
                    var color = '#800026';
                    for (var i=0; i<qualitativeColors.length; i++){
                        if (!qualitativeColors[i][1]){
                            color = qualitativeColors[i][0];
                            qualitativeColors[i][1] = feature.properties.agency_id;
                            break;
                        }
                    }
                    return {
                        fillColor: color,
                        weight: 2,
                        opacity: 1,
                        color: 'grey',
                        dashArray: '3',
                        fillOpacity: 0.3
                    };
                },
                onEachFeature: function (feature, layer) {
                    var p = feature.properties;
                    var contents = '<h5>Agency: '+p.agency_id+' ' +p.agency_name+
                                   '</h5>';
                    layer.bindPopup(contents);
                }
            });

        agencyFeatures.addLayer(feature);
        return feature._leaflet_id;
    }

    function addStopToMap(stop){
        var agency = $.grep(qualitativeColors, function(e) {
            return e[1] == stop.agency_id;
        });
        if (agency.length > 0)
            stop.color = agency[0][0];
        else
            stop.color = '#ff0a0f';

        var geojson = toGeoJson(stop)

        var feature = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng);
                },
                style: function(feature){
                    return {
                        fillColor: feature.properties.color,
                        color: 'white',
                        dashArray: '1',
                        fillOpacity: 0.8
                    }
                },
                onEachFeature: function (feature, layer) {
                    var p = feature.properties;
                    var contents = '<h5>Stop: '+p.stop_id+' ' +p.stop_name+
                                   '</h5>';
                    layer.bindPopup(contents);
                }
            });

        stopFeatures.addLayer(feature);
        return feature._leaflet_id;
    }


    function addTripToMap(trip){
        var route = $.grep(routes, function(e) {
            return e.route_id == trip.route_id;
        });
        if (route.length > 0)
            trip.route_color = '#' + route[0].route_color;
        else
            trip.route_color = '#fafa12';

        var geojson = toGeoJson(trip)

        var feature = L.geoJson(geojson, {
                style: function(feature){
                    return {color: feature.properties.route_color}
                },
                onEachFeature: function (feature, layer) {
                    var p = feature.properties;
                    var contents = '<h5>Trip: '+p.trip_id+' ' +p.trip_headsign+
                                   '</h5>';
                    layer.bindPopup(contents);
                }
            });

        tripFeatures.addLayer(feature);
        return feature._leaflet_id;
    }

    function addRouteToTable(route, layerID){
        $('#route-data tbody').append(
            '<tr data-category="routeFeatures" data-id="'+layerID+'">'+
            '<td>'+route.id+
            '</td><td>'+route.route_id+
            '</td><td>'+route.agency_id+
            '</td><td>'+route.route_short_name+
            '</td><td>'+route.route_long_name+
            '</td><td>'+route.route_type+
            '</td><td>'+route.route_desc+
            '</td><td>'+route.route_url+
            '</td><td style="background-color: #'+route.route_color+';">'+route.route_color+
            '</td></tr>');
    }

    function addAgencyToTable(agency, layerID){
        $('#agency-data tbody').append(
            '<tr data-category="agencyFeatures" data-id="'+layerID+'">'+
            '<td>'+agency.id+
            '</td><td>'+agency.agency_id+
            '</td><td>'+agency.agency_name+
            '</td><td>'+agency.agency_url+
            '</td><td>'+agency.agency_timezone+
            '</td><td>'+agency.agency_lang+
            '</td><td>'+agency.agency_phone+
            '</td><td>'+agency.agency_fare_url+'</td></tr>');
    }

    function addTripToTable(trip, layerID){
        $('#trip-data tbody').append(
            '<tr data-category="tripFeatures" data-id="'+layerID+'">'+
            '<td>'+trip.id+
            '</td><td>'+trip.trip_id+
            '</td><td>'+trip.agency_id+
            '</td><td>'+trip.route_id+
            '</td><td>'+trip.trip_headsign+
            '</td><td>'+trip.trip_short_name+
            '</td><td>'+trip.service_id+
            '</td><td>'+trip.direction_id+
            '</td><td>'+trip.block_id+
            '</td><td>'+trip.bikes_allowed+
            '</td><td>'+trip.wheelchair_accessible+
            '</td></tr>');
    }

    function addStopToTable(stop, layerID){
        $('#stop-data tbody').append(
            '<tr data-category="stopFeatures" data-id="'+layerID+'">'+
            '<td>'+stop.id+
            '</td><td>'+stop.stop_id+
            '</td><td>'+stop.agency_id+
            '</td><td>'+stop.stop_name+
            '</td><td>'+stop.stop_code+
            '</td><td>'+stop.stop_desc+
            '</td><td>'+stop.zone_id+
            '</td><td>'+stop.stop_url+
            '</td><td>'+stop.location_type+
            '</td><td>'+stop.stop_timezone+
            '</td><td>'+stop.parent_station+
            '</td><td>'+stop.wheelchair_accessible+
            '</td></tr>');
    }

    function loadObjects(options){
        $('#data-loader').show();
        var data = {'results_per_page': 500,
                   'page': options.page};
        if (options.filters){
            data.q = options.filters;
        }

        $.ajax({
            url: options.url,
            data: data,
            dataType: 'json'
        }).done(function(data){
            if (data.page + 1 <= data.total_pages){
                var opts = $.extend({}, options, {page: data.page+1});
                loadObjects(opts);
            }
            else{
                $('#data-loader').hide();
            }
            $.each(data.objects, function(index, elem){
                switch(options.type){
                    case 'agency':
                        var layerID = addAgencyToMap(elem);
                        addAgencyToTable(elem, layerID);
                        agencies.push(elem);
                        break;
                    case 'route':
                        var layerID = addRouteToMap(elem);
                        addRouteToTable(elem, layerID);
                        routes.push(elem);
                        break;
                    case 'trip':
                        var layerID = addTripToMap(elem);
                        addTripToTable(elem, layerID);
                        trips.push(elem);
                        break;
                    case 'stop':
                        var layerID = addStopToMap(elem);
                        addStopToTable(elem, layerID);
                        stops.push(elem);
                        break;
                }
            });
        }).error(function(e){
            console.log(e);
            $('#data-loader').hide();
        });
    }


    function buildFilters(elem){
        var selected_attribute = $(elem).find(':selected').val();
        var value = $(elem).find('input[type="text"]').val();

        return JSON.stringify({"filters":[{
                "name": selected_attribute,
                "op": "==",
                "val": value
            }]});
    }

    $('.form-inline input[type="checkbox"]').on('change', function(e){
        var toggle = $(this).is(':checked');
        $(this).parent().siblings('.form-group').children(':input').prop('disabled', !toggle);
    });

    $('#load-stops').on('click', function(e){
        e.preventDefault();
        $('#stop-data tbody').empty()
        stops = []
        stopFeatures.clearLayers();

        var filters;
        elem = $(this).parent();
        if ($(elem).find('input[type="checkbox"]').is(':checked')){
            filters = buildFilters(elem);
        }

        var options = {url: '/api/stop', page: 1, type: 'stop'}
        if (filters){
            options.filters = filters;
        }
        loadObjects(options);
    });

    $('#load-routes').on('click', function(e){
        e.preventDefault();
        $('#agency-data tbody').empty();

        var filters;
        elem = $(this).parent();
        if ($(elem).find('input[type="checkbox"]').is(':checked')){
            filters = buildFilters(elem);
        }

        routes = [];
        routeFeatures.clearLayers();

        var options = {url: '/api/route', page: 1, type: 'route'};
        if (filters){
            options.filters = filters;
        }
        loadObjects(options);
    });

    $('#load-agencies').on('click', function(e){
        e.preventDefault();
        $('#agency-data tbody').empty();

        var filters;
        elem = $(this).parent();
        if ($(elem).find('input[type="checkbox"]').is(':checked')){
            filters = buildFilters(elem);
        }

        agencies = [];
        agencyFeatures.clearLayers();

        for (var i=0; i<qualitativeColors.length; i++){
            qualitativeColors[i][1] = false;
        }

        var options = {url: '/api/agency', page: 1, type: 'agency'}
        if (filters){
            options.filters = filters;
        }
        loadObjects(options);
    });

    $('#load-trips').on('click', function(e){
        e.preventDefault();
        $('#trip-data tbody').empty();

        var filters;
        elem = $(this).parent();
        if ($(elem).find('input[type="checkbox"]').is(':checked')){
            filters = buildFilters(elem);
        }

        trips = [];
        tripFeatures.clearLayers();

        var options = {url: '/api/trip', page: 1, type: 'trip'}
        if (filters){
            options.filters = filters;
        }
        loadObjects(options);
    });

    $(document).on('click', '.table tr', function(){
        var group = $(this).data('category');
        var elemID = $(this).data('id');
        selectedFeature.clearLayers()
        var layer;
        switch (group){
            case 'stopFeatures':
                layer = stopFeatures.getLayer(elemID);
                break;
            case 'tripFeatures':
                layer = tripFeatures.getLayer(elemID);
                break;
            case 'routeFeatures':
                layer = routeFeatures.getLayer(elemID);
                break;
            case 'agencyFeatures':
                layer = agencyFeatures.getLayer(elemID);
                break;
        }

        if (layer instanceof L.GeoJSON) {
            options = layer.options;
            var clone = L.geoJson(layer.toGeoJSON(), options);
            selectedFeature.addLayer(clone);
        }
    });


});