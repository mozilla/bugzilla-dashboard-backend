from flask import Flask, jsonify
import requests, json, os, urllib, logging
from flask_cors import CORS

app = Flask(__name__, static_folder='./static')
CORS(app, resources=r'/api/*')
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

@app.route("/api/components/")
def getComponents():
	# Get components
	componentsUrl = os.path.join(SITE_ROOT, "static", "components.json")
	bzComponents = json.load(open(componentsUrl))
	return json.dumps(bzComponents[0])

@app.route('/api/components/update')
def updateComponents():
	# Get metrics data from static JSON file
	metricsUrl = os.path.join(SITE_ROOT, "static", "BZQueries.json")
	metrics = json.load(open(metricsUrl))

	# Fetch latest components from bugzilla
	componentsResponse = requests.get("https://bugzilla.mozilla.org/rest/product?type=accessible&include_fields=name&include_fields=components&exclude_fields=components.flag_types&exclude_fields=components.description")
	componentsData = componentsResponse.json()
	
	
	# Fetch products from the response
	products = componentsData['products']

	allComponents = {}

	# For local development, use only first product
	for product in products:
	#Production  
	# for product in products:
		# Fetch name of the product
		name = product['name']
		# Fetch all teh components for the given product
		components = product['components']
		# iterate over each component to fetch bug count for each metric from Metrics JSON file
		for component in components:
			if component['triage_owner'] != '':
				componentBugs = {}
				for metric in metrics[0]:
					metricBugs = {}
					metrics[0][metric].update( {'component' : component['name'] })
					metrics[0][metric].update( {'product' : name })
					# Encode URL for fetching bugcount using parameters from metrics
					url = urllib.parse.urlencode(metrics[0][metric])

					bzUrl = 'https://bugzilla.mozilla.org/rest/bug?count_only=1&'+url
					link =  'https://bugzilla.mozilla.org/buglist.cgi?'+url
					bugsData = requests.get(bzUrl)
					bugs = bugsData.json()
					metricBugs.update( {'count' : bugs['bug_count'] })
					metricBugs.update( {'link' : link })
					
					componentBugs[metric] = metricBugs

				key = name+'::'+component['name']
				allComponents[key] = componentBugs

		
	result = []
	result.append(allComponents)
	
	f = open('static/components.json', "w")
	f.write(json.dumps(result, separators=(',', ':')))
	f.close()
	
	return jsonify(success=True)



if __name__ == '__main__':
      app.run(host='0.0.0.0', port=2000)