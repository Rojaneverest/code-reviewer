# Windows GitLab Runner Setup for AI Code Reviewer

## Overview
This guide will help you configure a GitLab Runner on your Windows machine to execute the AI code review pipeline locally instead of using GitLab's hosted runners.

## Prerequisites
- Windows 10/11
- Python 3.8+ installed and in PATH
- PostgreSQL installed and running locally
- PowerShell (included with Windows)
- GitLab project with admin access to configure runners
- Your local machine should have access to your Databricks LLM endpoint

## Step 1: Install PostgreSQL (if not already installed)

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install PostgreSQL with default settings
3. Remember the password you set for the `postgres` user
4. Ensure PostgreSQL service is running

### Create the Rules Database

Open Command Prompt or PowerShell and run:
```cmd
# Connect to PostgreSQL (you'll be prompted for password)
psql -U postgres -h localhost

# Create the rules database
CREATE DATABASE rules;

# Exit psql
\q
```

## Step 2: Install GitLab Runner

1. Download gitlab-runner-windows-amd64.exe from [GitLab Runner releases](https://gitlab.com/gitlab-org/gitlab-runner/-/releases)
2. Create directory: `C:\GitLab-Runner`
3. Place the executable in `C:\GitLab-Runner\gitlab-runner.exe`
4. Run PowerShell as Administrator and execute:

```powershell
cd C:\GitLab-Runner
.\gitlab-runner.exe install
.\gitlab-runner.exe start
```

## Step 3: Register the Runner with Your GitLab Project

1. Go to your GitLab project → Settings → CI/CD → Runners
2. Click "New project runner"
3. Add tags: `ai-code-reviewer`
4. Copy the registration token
5. Run PowerShell as Administrator and execute:

```powershell
cd C:\GitLab-Runner
.\gitlab-runner.exe register
```

When prompted, provide:
- **GitLab instance URL**: `https://gitlab.com`
- **Registration token**: [paste the token from step 4]
- **Description**: `ai-code-reviewer`
- **Tags**: `ai-code-reviewer`
- **Executor**: `shell`
- **Shell**: `pwsh` (PowerShell)

## Step 4: Configure Environment Variables

### Option 1: PowerShell Script (Recommended)
Run PowerShell as Administrator and execute:
```powershell
.\setup_windows_runner_env.ps1
```

### Option 2: Batch Script
Run Command Prompt as Administrator and execute:
```cmd
setup_windows_runner_env.bat
```

### Option 3: Manual Setup
1. Open System Properties → Advanced → Environment Variables
2. Add the following System Variables:

```
# Database Configuration (Local PostgreSQL)
host=localhost
port=5432
dbname=rules
user=postgres
password=root

# Databricks Configuration
DATABRICKS_TOKEN=your_databricks_token
DATABRICKS_BASE_URL=https://dbc-your-workspace.cloud.databricks.com
DATABRICKS_ENDPOINT=/serving-endpoints/databricks-claude-sonnet-4/invocations
DATABRICKS_MODEL_NAME=databricks-claude-sonnet-4
DATABRICKS_TIMEOUT=60

# GitLab API Token
GITLAB_API_TOKEN=your_gitlab_personal_access_token
```

## Step 5: Set Up Database Schema and Rules

After configuring environment variables, set up the database schema:

```powershell
# Navigate to your project directory
cd path\to\your\code-reviewer

# Install Python dependencies
pip install -r requirements.txt

# Set up the database schema and insert rules
python database/setup_db.py

# Optionally, run the resilient database setup
python resilient_db_setup.py
```

## Step 6: Restart GitLab Runner Service

After setting environment variables, restart the GitLab Runner service:

```powershell
Restart-Service gitlab-runner
```

Or use Services.msc:
1. Open Services (services.msc)
2. Find "GitLab Runner"
3. Right-click → Restart

## Step 7: Test the Configuration

Run the configuration checker:
```powershell
python check_local_runner.py
```

## Step 8: Verify Runner Configuration

Your `C:\GitLab-Runner\config.toml` should look similar to:

```toml
concurrent = 1
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "ai-code-reviewer"
  url = "https://gitlab.com"
  id = 49633457
  token = "your-runner-token"
  executor = "shell"
  shell = "pwsh"
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
```

## Step 9: Test with a Merge Request

1. Create a merge request with SQL changes
2. Check that the pipeline runs on your local runner
3. Verify AI review comments are posted

## Troubleshooting

### Runner Not Picking Up Jobs
- Check runner status in GitLab project settings
- Verify tags match (`ai-code-reviewer`)
- Ensure runner is active and not paused

### Environment Variable Issues
- Variables must be set at System level (not User level)
- Restart GitLab Runner service after changing variables
- Check variables with: `Get-ChildItem Env:`

### PowerShell Execution Policy
If scripts don't run, set execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

### Python Not Found
- Ensure Python is installed and in PATH
- Test with: `python --version`
- Add Python to PATH if needed

## Security Considerations

1. **Environment Variables**: Set at system level for GitLab Runner service access
2. **Firewall**: Ensure Databricks endpoints are accessible
3. **Credentials**: Never commit tokens to version control
4. **Network**: Consider VPN requirements for corporate networks

## Logs and Debugging

GitLab Runner logs can be found in:
- Event Viewer → Windows Logs → Application
- Or run manually: `.\gitlab-runner.exe run`

## Example Working Configuration

Based on your setup, your runner should be configured with:
- **Name**: `ai-code-reviewer`
- **Executor**: `shell`
- **Shell**: `pwsh`
- **Tags**: `ai-code-reviewer`

This matches the GitLab CI configuration which uses the tag `ai-code-reviewer` for all jobs.
