# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from bugzilla_dashboard import app


@pytest.fixture
def client(request):
    test_client = app.test_client()
    return test_client


def test_new(client):
    response = client.get('/api/v1/components')
    assert response.status_code == 200
    if len(response.data) == 0:
        assert b'No data found' in response.data
    else:
        assert b'P1Defect' in response.data
