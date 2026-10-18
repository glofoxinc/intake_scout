# Board automation (free)

GitHub Actions polls AN/PIC every 15 minutes for tickets that just moved to start of work or Review / QA. Secrets on `glofoxinc/intake_scout` are already set.

Optional faster path: a Jira **Send web request** rule (needs project admin).

## Jira rule (optional)

1. Jira → **Project settings → Automation → Create rule** (AN, then clone for PIC).
2. **Trigger:** Issue transitioned to In Progress, Research, Build, QA Ready, Passed QA, or In Review.
3. **Then: Send web request**
   - URL: `https://api.github.com/repos/glofoxinc/intake_scout/dispatches`
   - Method: POST
   - Headers: `Accept` = `application/vnd.github+json`, `Authorization` = `Bearer YOUR_GITHUB_PAT`
   - Body:

```json
{
  "event_type": "intake-scout",
  "client_payload": {
    "issue_key": "{{issue.key}}"
  }
}
```

## Try one ticket

GitHub → Actions → **Intake Scout** → Run workflow → issue key `AN-XXXX`.

Or locally with `DRY_RUN=1`:

```powershell
python automation/handler.py AN-XXXX
```

The 15-minute poller is rules-only (title, label, size, description, AC from Jira text). Pictures still go through Cursor **Intake Scout for AN-XXXX**.
