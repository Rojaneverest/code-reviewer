# Local GitLab Runner Setup for AI Code Reviewer

## Overview
This guide will help you configure a GitLab Runner on your local machine to execute the AI code review pipeline locally instead of using GitLab's hosted runners.

## Prerequisites
- Docker installed on your local machine
- GitLab project with admin access to configure runners
- Your local machine should have access to your Databricks LLM endpoint

## Step 1: Install GitLab Runner

### On Linux (Ubuntu/Debian):
```bash
# Download the binary for your system
sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64

# Give it permissions to execute
sudo chmod +x /usr/local/bin/gitlab-runner

# Create a GitLab Runner user
sudo useradd --comment 'GitLab Runner' --create-home --shell /bin/bash gitlab-runner

# Install and run as service
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
sudo gitlab-runner start
```

### On macOS:
```bash
# Download and install
sudo curl --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-darwin-amd64
sudo chmod +x /usr/local/bin/gitlab-runner

# Install as service
cd ~
gitlab-runner install
gitlab-runner start
```

### On Windows:
1. Download gitlab-runner-windows-amd64.exe from GitLab
2. Rename to gitlab-runner.exe
3. Run as administrator:
```cmd
gitlab-runner.exe install
gitlab-runner.exe start
```

## Step 2: Register the Runner with Your GitLab Project

1. Go to your GitLab project → Settings → CI/CD → Runners
2. Expand the "Specific runners" section
3. Copy the registration token
4. Run the registration command:

```bash
sudo gitlab-runner register
```

When prompted, provide:
- **GitLab instance URL**: `https://gitlab.com` (or your GitLab instance URL)
- **Registration token**: [paste the token from step 3]
- **Description**: `Local AI Code Reviewer Runner`
- **Tags**: `local-runner,ai-review`
- **Executor**: `docker`
- **Default Docker image**: `python:3.9`

## Step 3: Configure Runner for Local Environment

Create a runner configuration that can access your local Databricks endpoint:

```bash
sudo nano /etc/gitlab-runner/config.toml
```

Add network configuration to allow access to your local services:

```toml
[[runners]]
  name = "Local AI Code Reviewer Runner"
  url = "https://gitlab.com/"
  token = "your-runner-token"
  executor = "docker"
  [runners.docker]
    tls_verify = false
    image = "python:3.9"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
    network_mode = "host"  # This allows access to localhost services
```

## Step 4: Environment Variables Setup

Set up environment variables on your local machine that the runner can access:

```bash
# Create environment file for the runner
sudo mkdir -p /etc/gitlab-runner/env
sudo nano /etc/gitlab-runner/env/ai-reviewer.env
```

Add your environment variables:
```bash
# Database Configuration (Supabase)
host=db.ziuhftkruvdlwiyfepop.supabase.co
port=5432
dbname=postgres
user=postgres
password=your_supabase_password

# Databricks Configuration (for local LLM access)
DATABRICKS_TOKEN=your_databricks_token
DATABRICKS_BASE_URL=your_databricks_workspace_url

# GitLab API Token
GITLAB_API_TOKEN=your_gitlab_personal_access_token
```

Update the runner configuration to use these environment variables:

```toml
[[runners]]
  name = "Local AI Code Reviewer Runner"
  url = "https://gitlab.com/"
  token = "your-runner-token"
  executor = "docker"
  [runners.docker]
    tls_verify = false
    image = "python:3.9"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
    network_mode = "host"
    env_file = ["/etc/gitlab-runner/env/ai-reviewer.env"]
```

## Step 5: Restart GitLab Runner

```bash
sudo gitlab-runner restart
```

## Step 6: Test the Setup

1. Create a test merge request with SQL changes
2. Check that the pipeline runs on your local runner (you should see it in GitLab under CI/CD → Jobs)
3. Monitor the job output to ensure it can access your local Databricks endpoint

## Troubleshooting

### Runner Not Picking Up Jobs
- Check runner status: `sudo gitlab-runner status`
- Verify runner is visible in GitLab project settings
- Ensure tags match between runner and CI configuration

### Network Access Issues
- Verify `network_mode = "host"` is set in config.toml
- Test Databricks connectivity from your local machine
- Check firewall settings

### Permission Issues
- Ensure gitlab-runner user has proper permissions
- Check Docker daemon accessibility

## Security Considerations

1. **Firewall**: Ensure your local machine's firewall allows necessary connections
2. **VPN**: If using corporate VPN, ensure Databricks endpoints are accessible
3. **Secrets**: Store sensitive tokens securely and never commit them to git
4. **Network**: Consider running on a dedicated machine or VM for isolation

## Alternative: Docker Compose Setup

For easier management, you can also run GitLab Runner in Docker:

```yaml
# docker-compose.yml for GitLab Runner
version: '3.8'
services:
  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner-local
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./gitlab-runner-config:/etc/gitlab-runner
    network_mode: host
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock
```

This approach provides better isolation and easier management of the runner configuration.
