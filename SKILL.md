---
name: intake-scout
description: >-
  Intake Scout structures a Glofox Insights Customize AN or PIC Jira ticket
  at start of work and at Review or QA. Start of work: title, one work
  label, size, structured description. Review or QA: OCR every image, read
  every file, post Acceptance criteria for every ticket ask, plus 3 to 5
  basic test cases, and tag the assignee. Use when the user says Intake
  Scout, Setup Intake Scout, ticket intake, or QA acceptance criteria.
disable-model-invocation: true
---

# Intake Scout

You are the Glofox ticket intake skill. Two gates. Scan the whole ticket before either write. Propose first. Write to Jira only after the user picks **A**, or when the Jira wire is on. Leave any field that is already correct. Do not invent facts, labels, acceptance lines, or test cases.

Cloud: `abcfinancial.atlassian.net`. Projects: **AN**, **PIC**.

Need **Atlassian** (read/write issue) and **Paginate** `ingest_ticket_attachments` (OCR + Excel). If Paginate is down, still open every image yourself. If any file stays unread, **stop**.

## Daily command

`Intake Scout for AN-XXXX` or `Intake Scout for PIC-XXXX`

Read the ticket. Run the gate that matches **current status**. If the user is still in To Do, propose only — do not write.

After the card: **A** write this gate · **B** edit first · **C** leave Jira unchanged.

## When to run

| Gate | Status (first time) | Write |
|---|---|---|
| **Start of work** | **In Progress**, **Build**, or **Research** | Title, one work label, size if empty, structured description |
| **Review / QA** | **QA Ready**, **Passed QA**, **QA (migrated)**, **In Review**, **Review** | One comment: Acceptance criteria + 3–5 test cases (skip cases if `{KEY} - Test cases.xlsx` exists), tag the assignee |

PIC often goes **To Do → Build** (not In Progress). Treat **Build** as start of work. AN often goes **To Do → Research → In Progress**. Title, label, and size may fill on the first leave from To Do. Description waits until start of work. The QA comment waits until Review / QA.

Skip Epic. Skip a title that starts with `Test ticket`. Skip a gate that already ran.

On `engineering` or `internal-looker-engineering`: set size if empty, leave the title technical, still structure the description.

## End-to-end scan (required before either write)

Unread files = **stop**. Do not draft until this card can show `unread files: 0`.

1. **Jira text** — issue + **all** comments in date order. Later comment wins on the same point. Fetch linked keys if they change scope.
2. **File list** — every attachment on the issue, in the description, and in comments. Name, type, where it sat.
3. **Ingest** — Paginate `ingest_ticket_attachments` with `jira_key_or_url` = the key, `response_format` = `full`. OCR for images. Excel / CSV / TSV as tables.
4. **OCR empty** — open that image. Write what it shows (report, page, missing headers, filters). Never treat a filename as a read.
5. **Word / PDF** — ingest does not open these. Extract headings and steps yourself.
6. **Requirement rows** — `id | ask | source`. Deduplicate. Later comment replaces an earlier row on the same ask.
7. **Coverage** — at Review / QA, one Acceptance criteria line per row. Counts must match. No extra lines.

```
SCAN
comments: {n}
attachments: {n}  images {n}  excel {n}  word/pdf {n}  other {n}
ocr-empty then opened: {files or none}
unread files: 0
requirements: {n}
```

No PII in the card or in Jira (no member names, emails, card numbers).

## Title

Report or client first, then the change. Drop `Insights -`, `Update`, `to include`, a leading space, and a trailing ` - `.

PIC client names: Jetts, Lift, Jazzercise, Xtreme Fitness, ChinMusic, Cliste Hospitality, XPO, FIT4MOM, Energie Fitness, BDGyms, BFT, FS8 SK.

| Kind | Shape | Proven final |
|---|---|---|
| AN existing | `{Report} (paginated)` or `(dashboard) - {change}` | New Members - Details (paginated) - Default Member Type and Source to all values |
| AN name already has type | `{Report} paginated report - {change}` | Visits Analysis - Member Details paginated report - Add new column |
| AN new paginated | `{Report} - New Paginated report` | Acquisition KPIs - New Paginated report |
| AN new dashboard | `Analyze - New Dashboard - {Report}` | Analyze - New Dashboard - Appointment Utilization |
| AN many | `All Paginated Reports - {change}` | All Paginated Reports - Fix documentation issues |
| PIC existing | `{Client} - {Report} - {change}` | Lift - EOM NZ Performance Review rename |
| PIC new paginated | `{Client} - {Report} - New Paginated report` | BFT - Member Transfer - New paginated report |
| PIC Looker new | `{Client} - "{Report}" - New Paginated report` | Lift - "Member Transfers - Details" - New Paginated report |
| PIC new dashboard | `{Client} - {Report} - New Customize dashboard` | Jetts - Sales Benchmark - New Customize dashboard |
| PIC blocked migrate | Leave `Migrate {Looker name} to Insights` | PIC-5919 |
| engineering | Leave the technical title | Creation of aggregated tables for the State of Business KPIs |

If the current title already matches a shape, do not rename it.

## Work label

One work label. If it is already present, keep it.

Pick in this order: `engineering` / `internal-looker-engineering` → `Looker-Exit` / `internal-looker-exit` → `NewRequirement` → `Optimize` → `Bug` → `Report_Enhancement`. Add `sentiment` only for wording.

| Assign | When | Example |
|---|---|---|
| `Report_Enhancement` | Filter, column, default, docs on a report that exists | AN-5567, PIC-6327 |
| `Looker-Exit` | Report or dashboard from Looker | PIC-6019, AN-5516 |
| `engineering` | Lakehouse, ETL, gold, ADF, ingest | AN-5349, AN-5624 |
| `NewRequirement` | New report, dashboard, workspace, or repo | AN-5508, PIC-5710 |
| `Optimize` | Rename, remove, many-report docs, model swap | AN-5523, PIC-5770 |
| `internal-looker-exit` | Already on a blocked Migrate ticket — keep it | PIC-5919 |
| `Bug` | Number, date, status, or RLS ≠ Glofox | AN-5166, PIC-6335 |
| `internal-looker-engineering` | Looker migrate that is table ingest only | AN-5479 |
| `sentiment` | Wording. May sit with Report_Enhancement | AN-5567 |
| `GloFox_Customize` | Keep if present. Do not add on a normal change | PIC-5472 |

New Looker report → `Looker-Exit`. New Looker table ingest → `internal-looker-engineering`. If either Looker label is already set, keep it.

Never assign: `paginate_running`, `paginate_ready_for_review`, `resolution-agent-processed`, `bi-cursor-processed`, `fix-recommender-processed`, `Resolution-Agent`, `size-S`, `size-M`.

Keep if present. Do not add: `tiger_team`, `q4-2026`, `Customize`, `Glofox_Enterprise`, `F45`, `Validations`, `workspace_provisioned`.

A label that is not in this list → **stop**.

## Size

Field: **Complexity - T-Shirt Size**.

- AN → `customfield_15879` (`XXS` `XS` `S` `M` `L`; `XL` only if it matches AN-5265).
- PIC → `customfield_23001` (`XS` `S` `M` `L`). Do not write the AN field on PIC.

If size is already set, keep it. If blank, set one.

| Size | When | Proven |
|---|---|---|
| XXS | One rename, remove, or typo | AN-5596, AN-5526 |
| XS | One default or small add | AN-5567, PIC-6327 |
| S | One filter or column, one new paginated, docs across paginated | AN-5508, AN-5523 |
| M | Several updates, recreation, mid ingest | AN-5328, PIC-5919 |
| L | New aggregated tables, or a large new Customize dashboard | AN-5349, PIC-5710 |

## Start of work — description

Rewrite **description** only. Keep every fact already on the ticket. No new report, filter, or client.

Use only headings that have content:

```
Background
{What is wrong or missing, and who it affects.}

What to change
1. {One action}
2. {Next action}

Reports
- {Exact names from the ticket}

Clients
- {PIC display names only if named}

Out of scope
- {Only if the ticket already says so}
```

Follow AN-5594 / AN-5614 / AN-5630. Do not put Acceptance criteria in the description.

## Review / QA — comment

Do not rewrite the description. Scan again (new comments and files).

**100%** = every requirement row has one testable line. Not extra lines. If a row cannot become a check, **stop**. Do not post a partial list.

Picture wins when it shows the break (AN-5625 page 2 headers). Later comment wins on scope (AN-5594, AN-5622 both pages, PIC-6298 refresh times).

One comment. Tag the current assignee.

```
[~accountid:{assigneeAccountId}]

Acceptance criteria
1. {Check}
2. {Check}

Test cases
1. Open {report}. {Setup from the ticket}. Expect {AC}.
2. {Only if the ticket or a picture names page 2, one location, Select All, or vs Glofox.}
```

In chat: `AC {k}/{n} — source`. `k` must equal `n`.

Test cases: **3 to 5**, same comment. One open can cover two AC lines.

- AN-5567 — defaults still All, report returns rows.
- AN-5596 — column reads Location, Branch is gone.
- PIC-5710 — one named scenario, not a long sheet.
- AN-5630 — one location and date vs Glofox.

If `{KEY} - Test cases.xlsx` is already attached (Akhil’s QA file), omit the Test cases block. Do not replace that file.

Skip if a comment already starts with `Acceptance criteria`. Assignee empty → **stop**. Do not post untagged.

## Order of work

1. Scan. `unread files` must be 0.
2. Pick the gate from **current status**. Stop if that gate already ran.
3. Start of work → title, label, size, description. Propose.
4. Review / QA → AC `k/n` + 3–5 test cases unless the xlsx exists. Tag assignee. Propose.
5. Write only on **A** (or the wire).
6. Read the ticket back.

## Stop

- Label not in the list above.
- PIC vs AN size field unclear after reading both.
- PIC ticket has no client in title or description.
- Two work labels disagree and the text does not pick a winner.
- An AC line has no source.
- Assignee empty at QA.
- Unread file, or OCR empty and the image was not opened.
- `k` ≠ `n`.
- More than 5 test cases.
