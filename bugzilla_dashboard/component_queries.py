# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
from collections import defaultdict

import structlog

from .query import Query

COMPONENTS_QUERY = os.path.join(
    os.path.dirname(__file__), "../queries/components_query.json"
)
OUTPUT_FILE = "product_component_data.json"
logger = structlog.get_logger(__name__)


class ComponentQuery(Query):
    def __init__(self, name, params):
        super().__init__(name, params)

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

    @staticmethod
    def build(out_dir="", compress=False):
        """Get all the bugs for the queries we've in component_queries.json"""
        with open(COMPONENTS_QUERY, "r") as In:
            data = json.load(In)

        results = defaultdict(lambda: {})
        for name, info in data.items():
            params = info["parameters"]
            params["include_fields"] = ["product", "component"]
            ComponentQuery(name, params).gather(results)

        Query.write(results, out_dir, OUTPUT_FILE, compress=compress)

        return results


if __name__ == "__main__":
    args = Query.get_args("Retrieve data from Bugzilla for product::component")
    ComponentQuery.build(out_dir=args.out_dir, compress=args.compress)
