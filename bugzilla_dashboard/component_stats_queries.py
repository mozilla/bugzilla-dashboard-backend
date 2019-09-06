# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
from collections import defaultdict

import structlog

from . import cli
from . import utils
from .query import Query

COMPONENTS_QUERY = os.path.join(
    os.path.dirname(__file__), "../queries/components_query.json"
)
OUTPUT_FILE = "product_component_stats_data.json"
logger = structlog.get_logger(__name__)


class ComponentStatsQuery(Query):
    def __init__(self, name, params):
        super().__init__(name, params)

    def transform(self, bugs):
        """Get stats for each product/component pair"""
        res = defaultdict(lambda: defaultdict(lambda: 0))
        for bug in bugs:
            assert {"product", "component", "cf_last_resolved", "creation_time"} <= set(
                bug.keys()
            )
            prod_comp = (bug["product"], bug["component"])
            last_resolved = utils.get_reference_date(bug["cf_last_resolved"])
            creation = utils.get_reference_date(bug["creation_time"])
            res[prod_comp][creation] += 1
            if last_resolved:
                res[prod_comp][last_resolved] -= 1

        return res

    def cumulate_stats(self, data):
        """Make a cumulated sum on counters"""
        # data is dictionary: date (sunday) => count
        res = []
        cumulated = 0
        for date, count in sorted(data.items()):
            cumulated += count
            res.append({"x": date.strftime("%Y-%m-%d"), "y": cumulated})
        return res

    def gather(self, results):
        """Transform the data to be used in the dashboard"""
        bugs = self.get_bugs()
        for (product, component), by_week in self.transform(bugs).items():
            prod_comp = f"{product}::{component}"
            results[prod_comp][self.name] = self.cumulate_stats(by_week)

    @staticmethod
    def build(out_dir="", compress=False):
        """Get all the bugs for the queries we've in component_queries.json"""
        with open(COMPONENTS_QUERY, "r") as In:
            data = json.load(In)

        results = defaultdict(lambda: {})
        for name, info in data.items():
            params = info["parameters"]

            # We need to get closed and open bugs to see the evolution
            if "resolution" in params:
                del params["resolution"]
            params["include_fields"] = [
                "product",
                "component",
                "creation_time",
                "cf_last_resolved",
            ]
            ComponentStatsQuery(name, params).gather(results)

        utils.write(results, out_dir, OUTPUT_FILE, compress=compress)

        return results


if __name__ == "__main__":
    args = cli.get_args("Retrieve stats from Bugzilla for product::component")
    ComponentStatsQuery.build(out_dir=args.out_dir, compress=args.compress)
