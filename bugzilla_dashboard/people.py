# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os

import requests
import structlog

from . import cli

logger = structlog.get_logger(__name__)

USERS_URL = "https://person.api.sso.mozilla.com/v2/users/id/all"


def get_access_token(iam_credentials):
    scope = {
        "classification": ["mozilla_confidential", "workgroup:staff_only"],
        "display": ["staff", "public", "none"],
    }
    scope = " ".join(
        f"{key}:{value}" for key, values in scope.items() for value in values
    )

    payload = {
        "client_id": iam_credentials["client_id"],
        "client_secret": iam_credentials["client_secret"],
        "audience": "api.sso.mozilla.com",
        "scope": scope,
        "grant_type": "client_credentials",
    }

    resp = requests.post("https://auth.mozilla.auth0.com/oauth/token", json=payload)
    if not resp.ok:
        logger.error("Invalid Auth response", error=resp.json())
        resp.raise_for_status()
    access = resp.json()

    assert "access_token" in access.keys()

    return access["access_token"]


def get_all_users(iam_access_token):
    headers = {"Authorization": f"Bearer {iam_access_token}"}
    params = {"active": "True", "connectionMethod": "ad"}

    while True:
        resp = requests.get(USERS_URL, headers=headers, params=params)
        if not resp.ok:
            logger.error("Invalid People API response", error=resp.content)
            resp.raise_for_status()

        data = resp.json()
        logger.info("Loaded batch of users", nb=len(data["users"]))
        for user in data["users"]:
            yield user

        params["nextPage"] = data["nextPage"]
        if params["nextPage"] is None:
            break


def get_phonebook_dump(output_dir, iam_credentials):
    # Retrieve access token from IAM
    iam_token = get_access_token(iam_credentials)

    new_data = {}

    # Browse full org with that token
    for user in get_all_users(iam_token):

        from pprint import pprint

        pprint(user)

        pass

        # new = {
        #    "mail": mail,
        #    "manager": {"cn": "", "dn": manager_mail},
        #    "ismanager": "TRUE" if ismanager else "FALSE",
        #    "isdirector": "TRUE" if isdirector else "FALSE",
        #    "cn": cn,
        #    "dn": dn,
        #    "bugzillaEmail": bugzillaEmail,
        #    "title": title,
        # }

    new_data = list(new_data.values())

    path = os.path.join(output_dir, "people.json")
    with open(path, "w") as out:
        json.dump(new_data, out, sort_keys=True, indent=4, separators=(",", ": "))


if __name__ == "__main__":
    args = cli.get_args("Build Org hierarchy")
    secrets = cli.load_secrets(args)
    assert "iam" in secrets, "Missing IAM auth"
    get_phonebook_dump(args.out_dir, secrets["iam"])
