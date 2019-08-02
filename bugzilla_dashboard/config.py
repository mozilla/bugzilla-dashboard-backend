# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Bugzilla URLs
BZ_HOST = 'https://bugzilla.mozilla.org'
COMPONENTS_URL = (
    BZ_HOST
    + '/rest/product?type=accessible&'
    + 'include_fields=name&include_fields=components&'
    + 'exclude_fields=components.flag_types&'
    + 'exclude_fields=components.description'
)
