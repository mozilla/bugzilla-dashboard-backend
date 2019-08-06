# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
from collections import defaultdict
from urllib.parse import urlencode

import structlog
from libmozdata.bugzilla import Bugzilla

COMPONENTS_QUERY = os.path.join(
    os.path.dirname(__file__), "../queries/components_query.json"
)
logger = structlog.get_logger(__name__)


class ComponentQuery:
    def __init__(self, name, params):
        super().__init__()
        self.name = name
        self.params = params

    def get_bz_params(self):
        """Get the parameters for the Bugzilla query"""
        return self.params

    def get_bz_search_url(self, extra={}):
        """Get the Bugzilla url for this search"""
        params = self.get_bz_params()
        if "include_fields" in params:
            del params["include_fields"]
        params.update(extra)
        return f"{Bugzilla.URL}/buglist.cgi?" + urlencode(params, doseq=True)

    def transform(self, bugs):
        """Get stats for each product/component pair"""
        res = {}
        for bug in bugs:
            assert "product" in bug and "component" in bug
            prod_comp = (bug["product"], bug["component"])
            res[prod_comp] = res.get(prod_comp, 0) + 1
        return res

    def gather(self, results):
        """Transform the data to be used in the dashboard"""
        bugs = self.get_bugs()
        for (product, component), count in self.transform(bugs).items():
            prod_comp = f"{product}::{component}"
            link = self.get_bz_search_url(
                extra={"product": product, "component": component}
            )
            results[prod_comp][self.name] = {"count": count, "link": link}

    def get_bugs(self):
        """Get the bugs"""
        bugs = []
        params = self.get_bz_params()

        def bughandler(bug, data):
            data.append(bug)

        logger.info(f"Get bugs for {self.name}: starting...")
        Bugzilla(params, bughandler=bughandler, bugdata=bugs).get_data().wait()
        logger.info(f"Get bugs for {self.name}: finished ({len(bugs)} retrieved).")
        return bugs

    @staticmethod
    def build(out=""):
        """Get all the bugs for the queries we've in component_queries.json"""
        with open(COMPONENTS_QUERY, "r") as In:
            data = json.load(In)

        results = defaultdict(lambda: {})
        for name, info in data.items():
            params = info["parameters"]
            params["include_fields"] = ["product", "component"]
            ComponentQuery(name, params).gather(results)

        if out:
            with open(out, "w") as Out:
                json.dump(results, Out)

        return results
