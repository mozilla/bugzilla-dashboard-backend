import sys
import requests
import urllib
import structlog
import json
from bugzilla_dashboard.config import BZ_HOST
from bugzilla_dashboard.config import COMPONENTS_URL

logger = structlog.get_logger(__name__)


# Get data from the give URL and transform return the result
def getData(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)


def update():
    data = getData(COMPONENTS_URL)

    products = data['products']
    with open('bugzilla_dashboard/components_query.json', 'r') as f:
        metrics = json.load(f)

    componentsData = {}

    # Loop through components and get bug count for each component
    for product in products:
        productName = product['name']

        components = product['components']

        # Get bugcount for each metrics of component
        for component in components:
            if(component['triage_owner'] == ''):
                logger.debug('Triage owner email id is missing')
            if component['triage_owner'] != '':
                componentBugs = {}
                for metric in metrics:
                    metrics[metric]['parameters'].update({
                        'component': component['name'],
                        'product': productName
                    })

                    # Encode URL for fetching bugcount using metrics
                    url = urllib.parse.urlencode(metrics[metric]['parameters'])

                    bzUrl = "{}/rest/bug?count_only=1&{}".format(
                        BZ_HOST, url)
                    link = "{}/buglist.cgi?{}".format(
                        BZ_HOST, url)

                    bugs = getData(bzUrl)

                    componentBugs[metric] = {
                        'count': bugs['bug_count'],
                        'link': link
                    }

                key = productName+'::'+component['name']
                componentsData[key] = componentBugs

    return componentsData
