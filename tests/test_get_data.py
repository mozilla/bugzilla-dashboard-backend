# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os

import requests
import responses

from bugzilla_dashboard.config import COMPONENTS_URL

MOCK_DIR = os.path.join(os.path.dirname(__file__), 'mocks')


@responses.activate
def test_getData():
    path = os.path.join(MOCK_DIR, 'components.json')
    responses.add(responses.GET, COMPONENTS_URL,
                  body=json.dumps(open(path).read()),
                  content_type='application/json')

    response = requests.get(COMPONENTS_URL)

    assert response.json() == open(path).read()
    assert response.status_code == 200
