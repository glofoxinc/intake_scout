# Install Intake Scout Cursor skills from this folder or a fresh clone.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$skills = Join-Path $env:USERPROFILE ".cursor\skills"
New-Item -ItemType Directory -Force -Path (Join-Path $skills "intake-scout") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $skills "setup-intake-scout") | Out-Null
Copy-Item -Force (Join-Path $root "SKILL.md") (Join-Path $skills "intake-scout\SKILL.md")
$setupSkill = Join-Path $root "setup-intake-scout.SKILL.md"
if (Test-Path $setupSkill) {
  Copy-Item -Force $setupSkill (Join-Path $skills "setup-intake-scout\SKILL.md")
}
Write-Host "Intake Scout installed. In Cursor say: Intake Scout for AN-XXXX"
