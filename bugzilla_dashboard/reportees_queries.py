# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
from collections import defaultdict

import structlog

from .query import Query

REPORTEES_QUERY = os.path.join(
    os.path.dirname(__file__), "../queries/reportees_query.json"
)
OUTPUT_FILE = "reportee_data.json"
logger = structlog.get_logger(__name__)


class ReporteeQuery(Query):
    def __init__(self, name, params):
        super().__init__(name, params)

    def transform(self, bugs):
        """Get stats for each reportee"""
        res = {}
        for bug in bugs:
            assert "assigned_to" in bug or "flags" in bug
            if "assigned_to" in bug:
                assignee = bug["assigned_to"]
                res[assignee] = res.get(assignee, 0) + 1
            else:
                for flag in bug["flags"]:
                    if (
                        flag.get("name", "") == "needinfo"
                        and flag["status"] == "?"
                        and "requestee" in flag
                    ):
                        requestee = flag["requestee"]
                        res[requestee] = res.get(requestee, 0) + 1
        return res

    def gather(self, results):
        """Transform the data to be used in the dashboard"""
        bugs = self.get_bugs()
        for reportee, count in self.transform(bugs).items():
            last = self.get_last_field_num()
            if self.name == "needinfo":
                extra = {
                    f"f{last}": "requestees.login_name",
                    f"o{last}": "equals",
                    f"v{last}": reportee,
                }
            else:
                extra = {
                    f"f{last}": "assigned_to",
                    f"o{last}": "equals",
                    f"v{last}": reportee,
                }
            link = self.get_bz_search_url(extra=extra)
            results[reportee][self.name] = {"count": count, "link": link}

    @staticmethod
    def build(out_dir="", compress=False):
        """Get all the bugs for the queries we've in reportees_query.json"""
        with open(REPORTEES_QUERY, "r") as In:
            data = json.load(In)

        results = defaultdict(lambda: {})
        for name, info in data.items():
            ReporteeQuery(name, info["parameters"]).gather(results)

        Query.write(results, out_dir, OUTPUT_FILE, compress=compress)

        return results


if __name__ == "__main__":
    args = Query.get_args("Retrieve data from Bugzilla for reportees")
    ReporteeQuery.build(out_dir=args.out_dir, compress=args.compress)
