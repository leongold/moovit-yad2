
import os
import json
import subprocess

import pickledb
from flask import Flask, request
from flask_cors import CORS
from requests_html import HTMLSession

from moovit import get_routes_proc


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

    result = get_routes_proc(src_addr, dst_addr)
    db.set(src_addr + dst_addr, result)
    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
