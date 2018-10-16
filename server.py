
import os
import json
import subprocess

from flask import Flask, request
from flask_cors import CORS
from requests_html import HTMLSession

from moovit import get_routes


app = Flask(__name__)
CORS(app)

cache = {}

@app.route('/query')
def main():
    global cache

    address_1 = request.args.get('address_1')
    address_2 = request.args.get('address_2')
    if not address_1 or not address_2:
        return "Requires address_1 and address_2 parameters."

    cached_result = cache.get((address_1, address_2))
    if cached_result:
        return cached_result

    proc = subprocess.Popen(
        [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'moovit.py'),
         address_1, address_2],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = proc.communicate()[0].decode('utf-8').strip()
    try:
        json.loads(result)
    except ValueError:
        result = [["no data", []]]
    result = json.dumps(result)
    cache[(address_1, address_2)] = result
    return result

if __name__ == '__main__':
    app.run()
