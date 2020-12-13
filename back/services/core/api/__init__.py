import os

from flask import Flask, jsonify, request
from parsers.database_handler import DatabaseReader
from settings import DB_HOST, DB_LOGIN, DB_DATABASE, DB_PASSWORD


app = Flask(__name__)

database_reader = DatabaseReader(DB_HOST, DB_LOGIN, DB_PASSWORD, DB_DATABASE)


def get_cities(places):
    cities_ids = (place.city_id for place in places)
    cities = database_reader.get_cities(cities_ids)
    response = {}
    for city in cities:
        response[city.id] = city.name
    return response

def get_orgs(places):
    orgs_ids = (place.org_id for place in places)
    orgs = database_reader.get_orgs(orgs_ids)
    response = {}
    for org in orgs:
        response[org.id] = org.name
    print(response)
    return response

@app.route('/list', methods=['GET'])
def list_places():
    try:
        viewport_str = request.args.get('viewport')
        sort = request.args.get('sort')
        if not viewport_str:
            return jsonify(ok=False, message="viewport arg required"), 400
        viewport_coords = [float(x) for x in viewport_str.split(',')]
        if not viewport_coords or len(viewport_coords) != 4:
            return jsonify(ok=False, message="viewport should be in format 'lon0,lat0,lon1,lat1'"), 400

        sort_close_to = None
        if sort:
            sort_close_to = [(viewport_coords[0] + viewport_coords[2]) / 2, (viewport_coords[1] + viewport_coords[3]) / 2]
        places = database_reader.get_places_in_rect(viewport_coords, sort_close_to)
        if len(places) == 0:
            return jsonify(ok=True, places=[]), 404
        cities = get_cities(places)
        orgs = get_orgs(places)
        response = jsonify(
            ok=True,
            places=[
                {
                    'organisation': orgs[place.org_id] if place.org_id in orgs else "Unknown",
                    'city': cities[place.city_id] if place.city_id in cities else "Unknown",
                    'address':place.address,
                    'coord':database_reader.convert_point_to_lat_lon(place.coord),
                    'url':place.url,
                    'pcr_test_price': place.pcr_test_price,
                    'antibodies_test_price': place.antibodies_test_price,
                    'time_of_completion': place.time_of_completion,
                } for place in places
            ]
        )
        return response, 200
    except:
        return jsonify(ok=False, message="Server internal error"), 500

@app.route('/')
def hello_world():
    return jsonify(message="Hello world test")

