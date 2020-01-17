# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os

import requests

from . import cli

USERS_URL = (
    "https://person.api.sso.mozilla.com/v2/users/id/all/by_attribute_contains",
)


def get_access_token(iam_credentials):
    scope = {
        "classification": [
            "mozilla_confidential",
            "workgroup:staff_only",
            "public",
            "workgroup",
        ],
        "display": ["staff", "ndaed", "vouched", "authenticated", "public", "none"],
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
    access = resp.json()

    assert "access_token" in access.keys()

    return access["access_token"]


def clean_data(d):
    if isinstance(d, dict):
        for k in ["metadata", "signature"]:
            if k in d:
                del d[k]

        for v in d.values():
            clean_data(v)
    elif isinstance(d, list):
        for v in d:
            clean_data(v)


def get_all_info(iam_access_token):
    headers = {"Authorization": f"Bearer {iam_access_token}"}
    params = {
        "staff_information.staff": "True",
        "active": "True",
        "fullProfiles": "True",
    }
    resp = requests.get(USERS_URL, headers=headers, params=params)
    data = resp.json()
    clean_data(data)

    next_page = data["nextPage"]

    while next_page is not None:
        print(f"{next_page}")
        params["nextPage"] = next_page
        resp = requests.get(USERS_URL, params=params, headers=headers)
        d = resp.json()
        clean_data(d)
        data["users"] += d["users"]
        next_page = d["nextPage"]

    del data["nextPage"]

    return data


def get_phonebook_dump(output_dir, iam_credentials):
    # Retrieve access token from IAM
    iam_token = get_access_token(iam_credentials)

    # Retrieve full payloads with that token
    data = get_all_info(iam_token)

    all_cns = {}
    all_dns = {}

    new_data = {}
    for person in data["users"]:
        person = person["profile"]
        if not person["access_information"]["hris"]["values"]:
            continue
        mail = person["access_information"]["hris"]["values"]["primary_work_email"]
        dn = person["identities"]["mozilla_ldap_id"]["value"]
        manager_mail = person["access_information"]["hris"]["values"][
            "managers_primary_work_email"
        ]
        if not manager_mail:
            manager_mail = mail

        _mail = person["identities"]["mozilla_ldap_primary_email"]["value"]
        assert mail == _mail

        ismanager = person["staff_information"]["manager"]["value"]
        isdirector = person["staff_information"]["director"]["value"]
        cn = "{} {}".format(person["first_name"]["value"], person["last_name"]["value"])
        bugzillaEmail = ""
        if "bugzilla_mozilla_org_primary_email" in person["identities"]:
            bugzillaEmail = person["identities"]["bugzilla_mozilla_org_primary_email"][
                "value"
            ]
        if not bugzillaEmail and "HACK#BMOMAIL" in person["usernames"]["values"]:
            bugzillaEmail = person["usernames"]["values"]["HACK#BMOMAIL"]

        if bugzillaEmail is None:
            bugzillaEmail = ""

        del person["usernames"]["values"]["LDAP-posix_id"]
        del person["usernames"]["values"]["LDAP-posix_uid"]
        im = list(person["usernames"]["values"].values())

        title = person["staff_information"]["title"]["value"]
        all_cns[mail] = cn
        all_dns[mail] = dn

        new = {
            "mail": mail,
            "manager": {"cn": "", "dn": manager_mail},
            "ismanager": "TRUE" if ismanager else "FALSE",
            "isdirector": "TRUE" if isdirector else "FALSE",
            "cn": cn,
            "dn": dn,
            "bugzillaEmail": bugzillaEmail,
            "title": title,
        }

        if im:
            new["im"] = im

        new_data[mail] = new

    for person in new_data.values():
        manager_mail = person["manager"]["dn"]
        manager_cn = all_cns[manager_mail]
        manager_dn = all_dns[manager_mail]
        person["manager"]["cn"] = manager_cn
        person["manager"]["dn"] = manager_dn

    new_data = list(new_data.values())

    path = os.path.join(output_dir, "people.json")
    with open(path, "w") as out:
        json.dump(new_data, out, sort_keys=True, indent=4, separators=(",", ": "))


if __name__ == "__main__":
    args = cli.get_args("Build Org hierarchy")
    secrets = cli.load_secrets(args)
    assert "iam" in secrets, "Missing IAM auth"
    get_phonebook_dump(args.out_dir, secrets["iam"])
