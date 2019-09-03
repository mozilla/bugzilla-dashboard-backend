# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import copy
import gzip
import json
import os
import re
from urllib.parse import urlencode

import structlog
from libmozdata.bugzilla import Bugzilla

BZ_FIELD_PAT = re.compile(r"^[fovj]([0-9]+)$")
logger = structlog.get_logger(__name__)


class Query:
    def __init__(self, name, params):
        super().__init__()
        self.name = name
        self.params = params

    def get_timeout(self):
        return 600

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
            params, bughandler=bughandler, bugdata=bugs, timeout=self.get_timeout()
        ).get_data().wait()
        logger.info(f"Get bugs for {self.name}: finished ({len(bugs)} retrieved).")
        return bugs

    @staticmethod
    def write(data, out_dir, file_name, compress=False):
        if not out_dir:
            return

        os.makedirs(out_dir, exist_ok=True)

        if compress:
            data = json.dumps(data)
            data = bytes(data, "utf-8")
            data = gzip.compress(data, compresslevel=9)
            with open(os.path.join(out_dir, file_name + ".gz"), "wb") as Out:
                Out.write(data)
        else:
            with open(os.path.join(out_dir, file_name), "w") as Out:
                json.dump(data, Out)

    @staticmethod
    def get_args(description):
        parser = argparse.ArgumentParser(description=description)

        parser.add_argument(
            "-o",
            "--output",
            dest="out_dir",
            action="store",
            default=os.environ.get("BZD_OUTPUT_PATH", ""),
            help="The output directory where to write the data",
        )

        parser.add_argument(
            "-c",
            "--compress",
            dest="compress",
            action="store_true",
            help="Compress data",
        )
        return parser.parse_args()
