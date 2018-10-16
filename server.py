
import os
import json
import subprocess

from pathos.multiprocessing import ProcessingPool as Pool

from flask import Flask, request
from flask_cors import CORS
from requests_html import HTMLSession

from moovit import get_routes


app = Flask(__name__)
CORS(app)

cache = {}


def _process(addr_1, addr_2):
    cached_result = cache.get((addr_1, addr_2))
    if cached_result:
        return cached_result

    proc = subprocess.Popen(
        [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'moovit.py'),
         addr_1, addr_2],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    result = proc.communicate()[0].decode('utf-8').strip()
    try:
        result = json.loads(result)
    except ValueError:
        result = [["no data", []]]
    return result


@app.route('/single')
def single():
    addr_1 = request.args.get('address_1')
    addr_2 = request.args.get('address_2')
    return json.dumps(_process(addr_1, addr_2))


@app.route('/batch')
def batch():
    dst = request.args.get('address_1')
    origins = request.args.get('origins').split(',')

    def proc(o):
        return _process(o, dst)

    with Pool(len(origins)) as p:
        results = p.map(proc, origins)

    return json.dumps(results)

if __name__ == '__main__':
    app.run()
