
import os
import json
import subprocess

from flask import Flask, request
from flask_cors import CORS
from requests_html import HTMLSession

from moovit import get_routes, FROM_CITY, FROM_ADDR


app = Flask(__name__)
CORS(app)


@app.route('/query')
def main():
    city = request.args.get('city')
    address = request.args.get('address')
    if not city or not address:
        return ""

    proc = subprocess.Popen(
        [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'moovit.py'),
         '{} {}'.format(address, city)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = proc.communicate()[0].decode('utf-8').strip()
    print("response:", json.dumps(result))
    return json.dumps(result)

if __name__ == '__main__':
    app.run()
