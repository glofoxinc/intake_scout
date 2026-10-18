"""Pick AN/PIC tickets that just hit start-of-work or Review/QA, then run handler."""

from __future__ import annotations

import json
import os
import urllib.parse

from handler import _req, run

JQL = (
    "project in (AN, PIC) AND issuetype != Epic AND "
    'status in ("In Progress","Build","Research","QA Ready","Passed QA",'
    '"QA (migrated)","In Review","Review") AND status CHANGED AFTER -30m '
    "ORDER BY updated DESC"
)


def recent_keys() -> list[str]:
    q = urllib.parse.quote(JQL, safe="")
    data = _req("GET", f"/rest/api/3/search/jql?jql={q}&maxResults=20&fields=key")
    return [i.get("key") for i in (data.get("issues") or []) if i.get("key")]


def main() -> None:
    keys = recent_keys()
    out = []
    for key in keys:
        out.append(run(key))
    print(json.dumps({"keys": keys, "results": out}, indent=2))


if __name__ == "__main__":
    if os.environ.get("ISSUE_KEY"):
        print(json.dumps(run(os.environ["ISSUE_KEY"].strip()), indent=2))
    else:
        main()
