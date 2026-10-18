---
name: setup-intake-scout
description: >-
  Install Intake Scout for this machine. Use when the user says Setup Intake
  Scout. Clone or refresh glofoxinc/intake_scout, copy SKILL.md, check Jira
  and Paginate. User does not run scripts.
disable-model-invocation: true
---

# Setup Intake Scout

When the user says **Setup Intake Scout**:

1. Get the pack:
   - If `C:\Users\LYal01\ZABC\projects\stable\intake-scout\SKILL.md` exists, use it.
   - Else clone or pull `https://github.com/glofoxinc/intake_scout` into `%USERPROFILE%\.cursor\skills-src\intake_scout`.
2. Run `setup.ps1` from that folder, or copy `SKILL.md` to `%USERPROFILE%\.cursor\skills\intake-scout\SKILL.md` and this file to `%USERPROFILE%\.cursor\skills\setup-intake-scout\SKILL.md`.
3. Confirm Atlassian Jira MCP can read an AN or PIC issue. If it cannot, ask the user to sign in once. Do not paste tokens into files.
4. Confirm Paginate `ingest_ticket_attachments` is available for picture text. If it is missing, say so — Review / QA still works if every image is opened by hand, but OCR will be slower.
5. Tell the user they are ready.

Daily: **Intake Scout for AN-XXXX** (or PIC-XXXX). Expect a start-of-work card or a Review / QA card. Jira does not change until they pick **A**.

Team guide: https://glofoxinc.github.io/intake_scout/DOCUMENTATION.html
