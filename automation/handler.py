"""Intake Scout Jira gate — rule-based writes for AN/PIC status changes.

Free path: Jira Automation (board) → GitHub Actions → this script.
Env: JIRA_BASE, JIRA_EMAIL, JIRA_API_TOKEN. Optional DRY_RUN=1.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from base64 import b64encode
from typing import Any

JIRA_BASE = (os.environ.get("JIRA_BASE") or "https://abcfinancial.atlassian.net").rstrip("/")
START_STATUSES = {"in progress", "build", "research"}
QA_STATUSES = {"qa ready", "passed qa", "qa (migrated)", "in review", "review"}
WORK_LABELS = {
    "Report_Enhancement",
    "Looker-Exit",
    "engineering",
    "NewRequirement",
    "Optimize",
    "internal-looker-exit",
    "Bug",
    "internal-looker-engineering",
    "sentiment",
    "GloFox_Customize",
}
AN_SIZE = "customfield_15879"
PIC_SIZE = "customfield_23001"


def _auth() -> str:
    email = os.environ.get("JIRA_EMAIL") or ""
    token = os.environ.get("JIRA_API_TOKEN") or ""
    if not email or not token:
        raise SystemExit("Set JIRA_EMAIL and JIRA_API_TOKEN")
    return "Basic " + b64encode(f"{email}:{token}".encode()).decode()


def _req(method: str, path: str, payload: dict | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{JIRA_BASE}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": _auth(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Jira {method} {path} failed: {exc.code} {exc.read()[:400]!r}") from exc


def _plain(adf_or_str: Any) -> str:
    if not adf_or_str:
        return ""
    if isinstance(adf_or_str, str):
        return adf_or_str
    bits: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "text" and node.get("text"):
                bits.append(str(node["text"]))
            for child in node.get("content") or []:
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(adf_or_str)
    return "\n".join(bits)


def _issue(key: str) -> dict:
    return _req(
        "GET",
        f"/rest/api/3/issue/{key}?fields=summary,description,status,labels,project,"
        f"issuetype,assignee,attachment,comment,{AN_SIZE},{PIC_SIZE}&expand=changelog",
    )


def _status_name(issue: dict) -> str:
    return ((issue.get("fields") or {}).get("status") or {}).get("name") or ""


def _seen_status(issue: dict, name: str) -> int:
    n = 0
    for hist in ((issue.get("changelog") or {}).get("histories") or []):
        for item in hist.get("items") or []:
            if item.get("field") == "status" and (item.get("toString") or "").lower() == name.lower():
                n += 1
    return n


def _gate(issue: dict) -> str | None:
    status = _status_name(issue).lower()
    itype = (((issue.get("fields") or {}).get("issuetype") or {}).get("name") or "").lower()
    summary = (issue.get("fields") or {}).get("summary") or ""
    if itype == "epic" or summary.lower().startswith("test ticket"):
        return None
    if status in START_STATUSES and _seen_status(issue, _status_name(issue)) <= 1:
        return "start"
    if status in QA_STATUSES and _seen_status(issue, _status_name(issue)) <= 1:
        return "qa"
    return None


def _pick_label(text: str, existing: list[str]) -> str | None:
    have = set(existing) & WORK_LABELS
    if have:
        return None
    t = text.lower()
    if any(w in t for w in ("ingest", "lakehouse", "gold_layer", "etl", "aggregated table")) and (
        "looker" in t or "migrate" in t
    ):
        return "internal-looker-engineering"
    if any(w in t for w in ("ingest", "lakehouse", "gold_layer", "etl", "aggregated table")):
        return "engineering"
    if "migrate" in t and "insights" in t:
        return "Looker-Exit"
    if "looker" in t:
        return "Looker-Exit"
    if any(w in t for w in ("new paginated", "new dashboard", "new customize", "new workspace", "github repo")):
        return "NewRequirement"
    if any(w in t for w in ("rename", "remove dashboard", "documentation issues")):
        return "Optimize"
    if any(w in t for w in ("mismatch", "incorrect", "does not match", "glofox")):
        return "Bug"
    return "Report_Enhancement"


def _clean_title(project: str, summary: str, text: str) -> str:
    s = (summary or "").strip()
    s = re.sub(r"^Insights\s*-\s*", "", s, flags=re.I)
    s = re.sub(r"^Update\s+", "", s, flags=re.I)
    s = re.sub(r"\s+-\s*$", "", s)
    if project == "AN" and re.search(r"all paginated", text, re.I):
        if not s.lower().startswith("all paginated"):
            change = re.sub(r"(?i)in paginated reports", "", s).strip(" -")
            return f"All Paginated Reports - {change}"
    return s


def _pick_size(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("aggregated table", "new customize dashboard")):
        return "L"
    if any(w in t for w in ("migrate", "ingestion", "several", "multiple")):
        return "M"
    if any(w in t for w in ("rename", "remove dashboard", "typo")):
        return "XXS"
    if any(w in t for w in ("default", "small add")):
        return "XS"
    return "S"


def _size_field(project: str) -> str:
    return AN_SIZE if project == "AN" else PIC_SIZE


def _size_already(fields: dict, project: str) -> bool:
    raw = fields.get(_size_field(project))
    if isinstance(raw, dict):
        return bool(raw.get("value"))
    return bool(raw)


def _size_option_id(key: str, field_id: str, value: str) -> str | None:
    meta = _req("GET", f"/rest/api/3/issue/{key}/editmeta")
    field = ((meta.get("fields") or {}).get(field_id)) or {}
    for opt in field.get("allowedValues") or []:
        if (opt.get("value") or "").upper() == value.upper():
            return opt.get("id")
    return None


def _structure_description(raw: str) -> str:
    body = (raw or "").strip()
    if not body:
        return body
    if body.startswith("Background"):
        return body
    return f"Background\n{body}\n\nWhat to change\n1. Complete the ask in Background.\n"


def _adf_comment(account_id: str, lines: list[str]) -> dict:
    content: list[dict] = [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "mention",
                    "attrs": {"id": account_id, "accessLevel": ""},
                },
                {"type": "text", "text": " "},
            ],
        },
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": "Acceptance criteria", "marks": [{"type": "strong"}]}],
        },
    ]
    for i, line in enumerate(lines, 1):
        content.append(
            {"type": "paragraph", "content": [{"type": "text", "text": f"{i}. {line}"}]}
        )
    return {"type": "doc", "version": 1, "content": content}


def _ac_lines(text: str) -> list[str]:
    bits = [b.strip(" -*") for b in re.split(r"[\n.]+", text) if len(b.strip()) > 20]
    out: list[str] = []
    for b in bits:
        if b.lower().startswith("currently") or "need" in b.lower() or "add" in b.lower() or "fix" in b.lower():
            out.append(b[:180])
        if len(out) >= 6:
            break
    return out or [text.strip()[:180] or "Confirm the ticket ask in the report."]


def _has_ac_comment(issue: dict) -> bool:
    for c in (((issue.get("fields") or {}).get("comment") or {}).get("comments") or []):
        if _plain(c.get("body")).lstrip().startswith("Acceptance criteria"):
            return True
    return False


def _has_tc_xlsx(issue: dict) -> bool:
    key = issue.get("key") or ""
    for a in (issue.get("fields") or {}).get("attachment") or []:
        name = (a.get("filename") or "").lower()
        if "test case" in name or name.startswith(key.lower() + " - test"):
            return True
    return False


def run(key: str) -> dict:
    issue = _issue(key)
    fields = issue.get("fields") or {}
    project = (fields.get("project") or {}).get("key") or ""
    if project not in {"AN", "PIC"}:
        return {"key": key, "skipped": "not AN/PIC"}
    gate = _gate(issue)
    if not gate:
        return {"key": key, "skipped": "not first start-of-work or QA status"}

    summary = fields.get("summary") or ""
    desc = _plain(fields.get("description"))
    comments = " ".join(_plain(c.get("body")) for c in ((fields.get("comment") or {}).get("comments") or []))
    text = f"{summary}\n{desc}\n{comments}"
    labels = list(fields.get("labels") or [])
    dry = os.environ.get("DRY_RUN") == "1"
    result: dict[str, Any] = {"key": key, "gate": gate, "dry_run": dry}

    if gate == "start":
        new_title = _clean_title(project, summary, text)
        new_label = _pick_label(text, labels)
        fields_update: dict[str, Any] = {}
        if new_title != summary:
            fields_update["summary"] = new_title
        if new_label:
            fields_update["labels"] = labels + [new_label]
        if not _size_already(fields, project):
            size = _pick_size(text)
            if project == "PIC" and size == "XXS":
                size = "XS"
            opt = _size_option_id(key, _size_field(project), size)
            if opt:
                fields_update[_size_field(project)] = {"id": opt}
            result["size"] = size
        structured = _structure_description(desc)
        if structured and structured != desc:
            fields_update["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": line} if line else {"type": "hardBreak"}]}
                    for line in structured.split("\n")
                ],
            }
        result["title"] = new_title
        result["label"] = new_label
        if fields_update and not dry:
            _req("PUT", f"/rest/api/3/issue/{key}", {"fields": fields_update})
        result["wrote"] = list(fields_update)

    if gate == "qa":
        if _has_ac_comment(issue):
            return {**result, "skipped": "Acceptance criteria already posted"}
        assignee = (fields.get("assignee") or {}).get("accountId")
        if not assignee:
            return {**result, "skipped": "no assignee to tag"}
        lines = _ac_lines(text)
        if not _has_tc_xlsx(issue):
            report = summary.split(" - ")[0]
            lines.append(f"Open {report} and confirm the acceptance lines above.")
        result["ac"] = lines
        if not dry:
            _req(
                "POST",
                f"/rest/api/3/issue/{key}/comment",
                {"body": _adf_comment(assignee, lines)},
            )
        result["wrote"] = ["comment"]

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python handler.py AN-XXXX")
    print(json.dumps(run(sys.argv[1].strip()), indent=2))
