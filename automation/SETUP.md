# Board automation (free)

Jira cannot open `SKILL.md`. The **board rule is free inside Jira**. The thinking runs on **GitHub Actions** (also free).

## Once

1. This repo is `https://github.com/glofoxinc/intake_scout`.
2. Repo **Settings → Secrets**: `JIRA_EMAIL`, `JIRA_API_TOKEN` (Atlassian API token from id.atlassian.com).
3. Optional repo **Variable**: `JIRA_BASE` = `https://abcfinancial.atlassian.net`.
4. Create a GitHub **fine-grained or classic PAT** that can `actions: write` / dispatch workflows. You will paste it only in the Jira rule header.

## Jira rule (AN project, then clone for PIC)

1. Jira → **Project settings → Automation → Create rule**.
2. **Trigger:** Issue transitioned  
   - From: To Do (optional)  
   - To: In Progress, Research, Build **or** QA Ready, Passed QA, In Review (two rules, or one rule with those statuses).
3. **If:** Project equals **AN** (second rule: **PIC**).  
   Issue type is not Epic.
4. **Then: Send web request**
   - URL: `https://api.github.com/repos/glofoxinc/intake_scout/dispatches`
   - Method: POST
   - Headers:
     - `Accept` = `application/vnd.github+json`
     - `Authorization` = `Bearer YOUR_GITHUB_PAT`
     - `X-GitHub-Api-Version` = `2022-11-28`
   - Body:

```json
{
  "event_type": "intake-scout",
  "client_payload": {
    "issue_key": "{{issue.key}}"
  }
}
```

5. Turn the rule **On**. Name it `Intake Scout — start of work` / `Intake Scout — QA`.

First time a ticket hits those statuses, GitHub runs `automation/handler.py` and writes title/label/size/description or the Acceptance criteria comment.

## Try one ticket without the board

On your PC (PowerShell):

```powershell
$env:JIRA_EMAIL = "you@abcfitness.com"
$env:JIRA_API_TOKEN = "your-token"
$env:DRY_RUN = "1"
python automation/handler.py AN-XXXX
```

Drop `DRY_RUN` only when the printed title/label look right.
