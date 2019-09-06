# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict
from datetime import datetime
from unittest.mock import MagicMock

from bugzilla_dashboard.component_stats_queries import ComponentStatsQuery


def test_transform():
    q = ComponentStatsQuery("foo", {})
    bugs = [
        {
            "product": "A",
            "component": "B",
            "creation_time": "2019-09-05",
            "cf_last_resolved": None,
        },
        {
            "product": "A",
            "component": "C",
            "creation_time": "2019-08-22",
            "cf_last_resolved": "2019-09-03",
        },
        {
            "product": "A",
            "component": "B",
            "creation_time": "2019-08-28",
            "cf_last_resolved": "2019-09-04",
        },
    ]

    stats = q.transform(bugs)
    # the dates correspond to the monday of the same week
    assert stats == {
        ("A", "B"): {datetime(2019, 8, 26): 1, datetime(2019, 9, 2): 0},
        ("A", "C"): {datetime(2019, 8, 19): 1, datetime(2019, 9, 2): -1},
    }


def test_gather():
    q1 = ComponentStatsQuery("foo", {})
    bugs = [
        {
            "product": "A",
            "component": "B",
            "creation_time": "2019-09-05",
            "cf_last_resolved": None,
        },
        {
            "product": "A",
            "component": "C",
            "creation_time": "2019-08-22",
            "cf_last_resolved": "2019-09-03",
        },
        {
            "product": "A",
            "component": "B",
            "creation_time": "2019-08-28",
            "cf_last_resolved": "2019-09-04",
        },
    ]
    q1.get_bugs = MagicMock(return_value=bugs)

    q2 = ComponentStatsQuery("bar", {})
    q2.get_bugs = MagicMock(return_value=bugs)

    results = defaultdict(lambda: {})
    q1.gather(results)
    q2.gather(results)

    assert results == {
        "A::B": {
            "foo": [{"x": "2019-08-26", "y": 1}, {"x": "2019-09-02", "y": 1}],
            "bar": [{"x": "2019-08-26", "y": 1}, {"x": "2019-09-02", "y": 1}],
        },
        "A::C": {
            "foo": [{"x": "2019-08-19", "y": 1}, {"x": "2019-09-02", "y": 0}],
            "bar": [{"x": "2019-08-19", "y": 1}, {"x": "2019-09-02", "y": 0}],
        },
    }
