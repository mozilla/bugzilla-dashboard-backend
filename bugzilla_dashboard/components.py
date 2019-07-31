# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import urllib

import requests
import structlog

from bugzilla_dashboard.config import BZ_HOST
from bugzilla_dashboard.config import COMPONENTS_URL

COMPONENTS_QUERY = os.path.join(
    os.path.dirname(__file__), "components_query.json"
)

COMPONENTS_QUERY = os.path.join(
    os.path.dirname(__file__), 'components_query.json'
)

logger = structlog.get_logger(__name__)


# Get data from the give URL and transform return the result
def getData(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()

    except requests.exceptions.RequestException as e:
        logger.debug("Something went wrong", error=e)
        raise Exception("Something went wrong {}".format(e))


def update():
    data = getData(COMPONENTS_URL)

    products = data['products']
    with open(COMPONENTS_QUERY, 'r') as f:
        metrics = json.load(f)
    componentsData = {}

    # Loop through components and get bug count for each component
    for product in products:
        productName = product["name"]

        components = product["components"]

        # Get bugcount for each metrics of component
        for component in components:
            if component['triage_owner'] == '':
                logger.debug('Triage owner email id is missing')
            else:
                componentBugs = {}
                for metric_key, metric in metrics.items():
                    metric['parameters'].update(
                        {'component': component['name'],
                            'product': productName}
                    )

                    # Encode URL for fetching bugcount using metrics
                    url = urllib.parse.urlencode(metric['parameters'])

                    bzUrl = '{}/rest/bug?count_only=1&{}'.format(BZ_HOST, url)
                    link = '{}/buglist.cgi?{}'.format(BZ_HOST, url)

                    bugs = getData(bzUrl)

                    componentBugs[metric_key] = {
                        'count': bugs['bug_count'],
                        'link': link,
                    }

                key = productName + '::' + component['name']
                componentsData[key] = componentBugs

    return componentsData
