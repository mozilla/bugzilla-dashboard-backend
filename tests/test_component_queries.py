# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict
from unittest.mock import MagicMock

from bugzilla_dashboard.component_queries import ComponentQuery


def test_bz_search_url():
    q = ComponentQuery("foo", {"a": 1, "b": 2})
    assert q.get_bz_search_url() == "https://bugzilla.mozilla.org/buglist.cgi?a=1&b=2"
    assert (
        q.get_bz_search_url({"c": 3})
        == "https://bugzilla.mozilla.org/buglist.cgi?a=1&b=2&c=3"
    )


def test_transform():
    q = ComponentQuery("foo", {})
    bugs = [
        {"product": "A", "component": "B"},
        {"product": "A", "component": "C"},
        {"product": "D", "component": "B"},
        {"product": "A", "component": "B"},
        {"product": "D", "component": "B"},
        {"product": "E", "component": "F"},
    ]

    stats = q.transform(bugs)
    assert stats == {("A", "B"): 2, ("A", "C"): 1, ("D", "B"): 2, ("E", "F"): 1}


def test_gather():
    q1 = ComponentQuery("foo", {"a": 1})
    bugs = [
        {"product": "A", "component": "B"},
        {"product": "A", "component": "B"},
        {"product": "D", "component": "B"},
        {"product": "E", "component": "F"},
    ]
    q1.get_bugs = MagicMock(return_value=bugs)

    q2 = ComponentQuery("bar", {"b": 1})
    bugs = [
        {"product": "A", "component": "B"},
        {"product": "A", "component": "B"},
        {"product": "D", "component": "B"},
        {"product": "A", "component": "B"},
    ]
    q2.get_bugs = MagicMock(return_value=bugs)

    results = defaultdict(lambda: {})
    q1.gather(results)
    q2.gather(results)

    assert results == {
        "A::B": {
            "foo": {
                "count": 2,
                "link": "https://bugzilla.mozilla.org/buglist.cgi?a=1&product=A&component=B",
            },
            "bar": {
                "count": 3,
                "link": "https://bugzilla.mozilla.org/buglist.cgi?b=1&product=A&component=B",
            },
        },
        "D::B": {
            "foo": {
                "count": 1,
                "link": "https://bugzilla.mozilla.org/buglist.cgi?a=1&product=D&component=B",
            },
            "bar": {
                "count": 1,
                "link": "https://bugzilla.mozilla.org/buglist.cgi?b=1&product=D&component=B",
            },
        },
        "E::F": {
            "foo": {
                "count": 1,
                "link": "https://bugzilla.mozilla.org/buglist.cgi?a=1&product=E&component=F",
            }
        },
    }
