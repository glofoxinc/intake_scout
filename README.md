# Intake Scout

Share pack for the **Intake Scout** Cursor skill — structure the Jira ticket at start of work, then post acceptance checks at Review / QA.

| File | Purpose |
|------|---------|
| [DOCUMENTATION.html](./DOCUMENTATION.html) | Team guide (source in repo) |
| **Team guide (browser)** | https://glofoxinc.github.io/intake_scout/DOCUMENTATION.html |
| [SKILL.md](./SKILL.md) | Cursor skill reference |

## Setup (once, about 5 minutes)

Clone https://github.com/glofoxinc/intake_scout then in Cursor say **Setup Intake Scout**. If it needs Jira, it will ask once.

Then try: **Intake Scout for AN-XXXX** (your real ticket). Reply **A** to write, **C** to leave Jira unchanged.

## Daily

- Start of work (AN **In Progress**, PIC **Build**): title, label, size, description.
- Review / QA: acceptance criteria + a few test cases, tags the assignee.

Pair with **Semantic Scout** before you raise the PR.

## Board automation (free)

GitHub Actions polls AN/PIC every 15 minutes. Optional Jira rule: [automation/SETUP.md](./automation/SETUP.md).
