from flask import Flask, jsonify, request
import requests, json, os, urllib, logging
from flask_cors import CORS
from . import routes

app = Flask(__name__, static_folder='../static')
CORS(app, resources=r'/api/*')
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

# List all reportees
@routes.route('/api/reportees/<email>')
def getReporteesData(email):
	reportees = {}
	reporteesUrl = os.path.join(SITE_ROOT, "../static", "reportees.json")
	reporteesData = json.load(open(reporteesUrl))

	for reportee in reporteesData:
		if(reportee['email'] == email):
			key = reportee['bugzillaEmail'] if 'bugzillaEmail' in reportee.keys() else reportee['email']
			reportees[key] = reportee['data']

	# inf = findReportees(reporteesData, email, reportees)
	data = findReportees(reporteesData, email, reportees)
	return json.dumps(data)

# Find all reportee for a given Email
def findReportees(data, email, reporteesArray):
	allReportees = []
	for reportee in data:
		if(reportee['manager'] == email):
			allReportees.append(reportee)
			key = reportee['bugzillaEmail'] if 'bugzillaEmail' in reportee.keys() else reportee['email']
			reporteesArray[key] = reportee['data']

	if(len(allReportees) > 0):
		for currentReportee in allReportees:
			findReportees(data, currentReportee['email'], reporteesArray)
	return reporteesArray


# update all reportees data
@routes.route('/api/reportees/update')
def updateReporteesData():
	reporteesUrl = os.path.join(SITE_ROOT, "../static", "reportees.json")
	reportees = json.load(open(reporteesUrl))

	# Get metrics data from static JSON file
	metricsUrl = os.path.join(SITE_ROOT, "../static", "reporteesMetrics.json")
	metrics = json.load(open(metricsUrl))

	for reportee in reportees:
		email = reportee['bugzillaEmail'] if 'bugzillaEmail' in reportee.keys() else reportee['email']
		for metric in metrics[0]:
			metricBugs = {}
			if(metric == 'needinfo'):
				metrics[0][metric]['parameterGenerator']['v1'] = email
			else:
				metrics[0][metric]['parameterGenerator']['email1'] = email 

			url = urllib.parse.urlencode(metrics[0][metric]['parameterGenerator'])
			
			bzUrl = 'https://bugzilla.mozilla.org/rest/bug?count_only=1&'+url
			link =  'https://bugzilla.mozilla.org/buglist.cgi?'+url

			bugsData = requests.get(bzUrl).json()
			
			reportee['data'][metric]['count'] = bugsData['bug_count']
			reportee['data'][metric]['link'] = link

	f = open('static/reportees.json', "w")
	f.write(json.dumps(reportees, separators=(',', ':')))
	f.close()
	return jsonify(success=True)

# Get reportees for a given OrgStructure
# Check if all the email Ids present in the JSON file.
# if not, add that email id to JSon and return data

@routes.route('/api/reportees/',methods = ['POST'])
def getReportees():
	reporteesUrl = os.path.join(SITE_ROOT, "../static", "reportees.json")
	reportees = json.load(open(reporteesUrl))

	metricsUrl = os.path.join(SITE_ROOT, "../static", "reporteesMetrics.json")
	metrics = json.load(open(metricsUrl))

	orgStructure = request.get_json()
	data = orgStructure['data'];
	ldapEmail = '';

	emails = []

	for value in data:
		if(value == orgStructure['email']):
			ldapEmail = data[value]['mail']
		emails.append({
			'email' : data[value]['mail'],
			'manager' : data[value]['manager']['dn'] if data[value]['manager'] is not None else None 
		})

	
	# Check if email exists in the reportees list
	for email in emails:

		reporteeData = {}
		if not any(reportee['email'] == email['email'] for reportee in reportees):

			reporteeData['email'] = email['email'];

			if(email['manager'] is not None):
				splittedText = email['manager'].split('=')
				managerEmail = splittedText[1].split(',')
				reporteeData['manager'] = managerEmail[0];
			else:
				reporteeData['manager'] = None			

			metricsData = {}
			for metric in metrics[0]:
				metricBugs = {}
				if(metric == 'needinfo'):
					metrics[0][metric]['parameterGenerator']['v1'] = email['email']
				else:
					metrics[0][metric]['parameterGenerator']['email1'] = email['email'] 

				url = urllib.parse.urlencode(metrics[0][metric]['parameterGenerator'])
				
				bzUrl = 'https://bugzilla.mozilla.org/rest/bug?count_only=1&'+url
				link =  'https://bugzilla.mozilla.org/buglist.cgi?'+url

				bugsData = requests.get(bzUrl).json()
			
				metricBugs.update( {'count' : bugsData['bug_count'] })
				metricBugs.update( {'link' : link })

				metricsData[metric] = metricBugs;

			reporteeData['data'] = metricsData

			reportees.append(reporteeData)

		
	f = open('static/reportees.json', "w")
	f.write(json.dumps(reportees, separators=(',', ':')))
	f.close()

	return getReporteesData(ldapEmail)
