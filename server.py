#!/usr/bin/python3
import logging
import os
import json
import subprocess
import traceback

import pickledb
from flask import Flask, request
from flask_cors import CORS
from requests_html import HTMLSession

from common import setup_logging
from lat_lon import get_lat_lon
from moovit.routes import get_routes_proc
from moovit.routes import next_weekday_at_8_am_timestamp
from moovit.routes import ts_repr


db = pickledb.load('db', True)
logger = setup_logging(__name__)
app = Flask(__name__)
CORS(app)


def _get_addresses(request):
    if request.method == 'POST':
        f = request.form.get
    else:
        f = request.args.get
    return f('src_addr'), f('dst_addr')


@app.route('/', methods = ['POST', 'GET'])
def main():
    if request.method == 'POST':
        args = request.form
    else:
        args = request.args

    src_addr = args.get('src_addr')
    dst_addr = args.get('dst_addr')
    timestamp = args.get('timestamp', next_weekday_at_8_am_timestamp())

    logger.info("recieved {} request, addresses: {}, {} ({})".format(
        request.method, src_addr, dst_addr, timestamp)
    )
    if not src_addr or not dst_addr:
        err = "src_addr and dst_addr are required"
        logger.error(err)
        return json.dumps({"error": err})

    try:
        lat_lon_x = get_lat_lon(src_addr)
        lat_lon_y = get_lat_lon(dst_addr)
    except Exception as e:
        err = "failed to get coordinates:\n" + traceback.format_exc() 
        logger.error(err)
        return json.dumps({"error": "failed to get coordinates"})

    key = (lat_lon_x, lat_lon_y, timestamp)
    cached_result = db.get(json.dumps(key))
    if cached_result:
        logger.info("returning cached result")
        return json.dumps(
            {"timestamp": timestamp,
             "routes": cached_result,
             "date": ts_repr(timestamp)}
        )

    try:
        routes = get_routes_proc(lat_lon_x, lat_lon_y, timestamp)
    except Exception as e:
        err = "failed to get route:\n" + traceback.format_exc()
        logger.error(err)
        return json.dumps({"error": "failed to get route"})
    try:
        result = json.dumps(
            {"timestamp": timestamp,
             "routes": routes,
             "date": ts_repr(timestamp)}
        )
    except Exception as e:
        err = "failed to json dump: " + str(e)
        logger.error(err)
        return json.dumps({"error": "failed to serialize result"})

    logger.info("saving and returning route")
    db.set(json.dumps(key), routes)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0')
