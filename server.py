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
from moovit.routes import get_routes_proc


db = pickledb.load('db', True)
app = Flask(__name__)
CORS(app)


@app.route('/', methods = ['POST', 'GET'])
def main():
    if request.method == 'POST':
        f = request.form.get
    else:
        f = request.args.get
    src_addr = f('src_addr')
    dst_addr = f('dst_addr')

    cached_result = db.get(src_addr + dst_addr)
    if cached_result:
        return json.dumps(cached_result)

    try:
        routes = get_routes_proc(src_addr, dst_addr)
    except Exception as e:
        logging.error(
            "failed to get route for {} -> {}: {}".format(
                dst_addr, src_addr, traceback.format_exc()
            )
        )
        return json.dumps({"error'": str(e)})
    try:
        result = json.dumps(routes)
    except Exception as e:
        logging.error("failed to convert result to json: " + str(e))
        return json.dumps({"error'": str(e)})

    db.set(src_addr + dst_addr, routes)
    return result


if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0')
