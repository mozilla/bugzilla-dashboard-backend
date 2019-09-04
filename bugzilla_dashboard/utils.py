# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import gzip
import json
import os
from datetime import datetime


def write(data, out_dir, file_name, compress=False):
    if not out_dir:
        return

    os.makedirs(out_dir, exist_ok=True)

    data = add_metadata(data)

    path = os.path.join(out_dir, file_name)
    if compress:
        data = json.dumps(data)
        data = bytes(data, "utf-8")
        data = gzip.compress(data, compresslevel=9)
        with open(f"{path}.gz", "wb") as Out:
            Out.write(data)
    else:
        with open(path, "w") as Out:
            json.dump(data, Out)


def add_metadata(data):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    data["metadata"] = {"time": now}
    return data
