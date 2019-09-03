# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import copy
import re
from urllib.parse import urlencode

import structlog
from libmozdata.bugzilla import Bugzilla

BZ_FIELD_PAT = re.compile(r"^[fovj]([0-9]+)$")
logger = structlog.get_logger(__name__)


class Query:

    TIMEOUT = 600

    def __init__(self, name, params):
        super().__init__()
        self.name = name
        self.params = params

    def get_bz_params(self):
        """Get the parameters for the Bugzilla query"""
        return self.params

    def get_bz_search_url(self, extra={}):
        """Get the Bugzilla url for this search"""
        params = copy.deepcopy(self.get_bz_params())
        if "include_fields" in params:
            del params["include_fields"]
        params.update(extra)
        return f"{Bugzilla.URL}/buglist.cgi?" + urlencode(params, doseq=True)

    def get_last_field_num(self):
        s = set()
        for k in self.params.keys():
            m = BZ_FIELD_PAT.match(k)
            if m:
                s.add(int(m.group(1)))

        x = max(s) + 1 if s else 1
        return str(x)

    def get_bugs(self):
        """Get the bugs"""
        bugs = []
        params = self.get_bz_params()

        def bughandler(bug, data):
            data.append(bug)

        logger.info(f"Get bugs for {self.name}: starting...")
        Bugzilla(
            params, bughandler=bughandler, bugdata=bugs, timeout=Query.TIMEOUT
        ).get_data().wait()
        logger.info(f"Get bugs for {self.name}: finished ({len(bugs)} retrieved).")
        return bugs
