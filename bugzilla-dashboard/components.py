from . import config
import requests, urllib

componentsUrl = config.settings['COMPONENTS_URL']

# Get data from the give URL and transform return the result
def getData(url):
    componentsResponse = requests.get(url)
    return componentsResponse.json()

def update():
    data = getData(componentsUrl)
    products = data['products']
    metrics = config.BZ_QUERIES
    
    componentsData = {}

    # Loop through components and get bug count for each component
    for product in products:
        productName= name = product['name']

        components = product['components']
        tempData = components[2:3]

        # Get bugcount for each metrics of component
        for component in tempData:
            if component['triage_owner'] != '':
                componentBugs = {}
                for metric in metrics:
                    metricBugs = {}
                    metrics[metric]['parameters'].update( {'component' : component['name'] })
                    metrics[metric]['parameters'].update( {'product' : productName })
                    
                    # Encode URL for fetching bugcount using parameters from metrics
                    url = urllib.parse.urlencode(metrics[metric]['parameters'])

                    bzUrl = config.settings['BZ_HOST']+'/rest/bug?count_only=1&'+url
                    link =  config.settings['BZ_HOST']+'/buglist.cgi?'+url

                    bugsData = requests.get(bzUrl)
                    bugs = bugsData.json()
                    metricBugs.update( {'count' : bugs['bug_count'] })
                    metricBugs.update( {'link' : link })
                    componentBugs[metric] = metricBugs
                    
                key = productName+'::'+component['name']
                componentsData[key] = componentBugs
        
    return componentsData