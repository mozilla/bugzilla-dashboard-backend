# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import os


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
        "-c", "--compress", dest="compress", action="store_true", help="Compress data"
    )
    return parser.parse_args()
