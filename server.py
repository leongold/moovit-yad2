
import os
import json
import subprocess

from flask import Flask, request
from flask_cors import CORS
from requests_html import HTMLSession

from moovit import get_routes


app = Flask(__name__)
CORS(app)


@app.route('/query')
def main():
    address_1 = request.args.get('address_1')
    address_2 = request.args.get('address_2')
    if not address_1 or not address_2:
        print(address_1, address_2)
        return
    proc = subprocess.Popen(
        [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'moovit.py'),
         address_1, address_2],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = proc.communicate()[0].decode('utf-8').strip()
    print("response:", json.dumps(result))
    return json.dumps(result)

if __name__ == '__main__':
    app.run()
