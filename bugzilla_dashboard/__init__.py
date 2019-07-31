# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import Flask
import os
from flask_cors import CORS
from . import components

app = Flask(__name__)
CORS(app, resources=r"/api/*")
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


@app.errorhandler(404)
def not_found(error):
    return {
        'status': 404,
        'message': 'Not found'
    }


# Get component data
@app.route("/api/v1/components")
def getComponents():
    if not os.path.exists(STATIC_DIR):
        createDir()

    componentsPath = os.path.join(STATIC_DIR, 'components.json')
    if os.path.getsize(componentsPath) > 0:
        with open(componentsPath, "r") as f:
            return json.load(f)
    else:
        return "No data found"

# Update components data
@app.route('/update')
def update():
	if not os.path.exists('static'):
		createDir()

	data = components.update()

	f = open('static/components.json', "w")
	f.write(json.dumps(data, separators=(',', ':')))
	f.close()

	return 'Result updated'

# Create static directory and components.json file for local development
def createDir():
    os.makedirs(STATIC_DIR)
    f = open(os.path.join(STATIC_DIR, 'components.json'), "w")
    f.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
