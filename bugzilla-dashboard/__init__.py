from flask import Flask, jsonify, json
import os
from flask_cors import CORS
from . import components

app = Flask(__name__, static_folder='../static')
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

@app.errorhandler(404)
def not_found(error):
    return {
        "status": 404,
        "message": "Not found" 
    }

# Get component data
@app.route('/data')
def data():
	if not os.path.exists('static'):
		createDir()

	componentsUrl = os.path.join(SITE_ROOT, "../static", "components.json")
	if os.path.getsize(componentsUrl) > 0:
		bzComponents = json.load(open(componentsUrl))
		return bzComponents
	else:
		return 'No data found'

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
	os.makedirs('static')
	file = open(os.path.join('static', 'components.json'), 'w')
	file.close()
	return 'created'

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=3000)