#!/bin/bash

# Local GitLab Runner Environment Setup Script
# This script helps configure environment variables for the local GitLab runner

set -e

echo "🚀 GitLab Runner Local Environment Setup"
echo "========================================"

# Check if running as root (needed for GitLab runner configuration)
if [[ $EUID -eq 0 ]]; then
    ENV_FILE="/etc/gitlab-runner/env/ai-reviewer.env"
    CONFIG_FILE="/etc/gitlab-runner/config.toml"
else
    echo "⚠️  This script should be run with sudo for system-wide GitLab runner configuration"
    echo "Running in user mode - creating local environment file"
    ENV_FILE="$HOME/.gitlab-runner-env"
    CONFIG_FILE="$HOME/.gitlab-runner-config.toml"
fi

# Create directory for environment file
mkdir -p "$(dirname "$ENV_FILE")"

echo "📝 Creating environment file: $ENV_FILE"

# Function to prompt for environment variable
prompt_var() {
    local var_name="$1"
    local description="$2"
    local is_secret="$3"
    local current_value=""
    
    # Check if variable already exists
    if [[ -f "$ENV_FILE" ]] && grep -q "^${var_name}=" "$ENV_FILE"; then
        current_value=$(grep "^${var_name}=" "$ENV_FILE" | cut -d'=' -f2-)
        if [[ "$is_secret" == "true" && -n "$current_value" ]]; then
            current_display="[HIDDEN - already set]"
        else
            current_display="$current_value"
        fi
        echo "Current value for $var_name: $current_display"
    fi
    
    if [[ "$is_secret" == "true" ]]; then
        echo -n "$description: "
        read -s value
        echo
    else
        echo -n "$description: "
        read value
    fi
    
    if [[ -n "$value" ]]; then
        # Remove existing entry and add new one
        grep -v "^${var_name}=" "$ENV_FILE" 2>/dev/null > "${ENV_FILE}.tmp" || touch "${ENV_FILE}.tmp"
        echo "${var_name}=${value}" >> "${ENV_FILE}.tmp"
        mv "${ENV_FILE}.tmp" "$ENV_FILE"
    fi
}

echo
echo "🗄️  Database Configuration (Supabase)"
echo "-----------------------------------"
prompt_var "host" "Database host (e.g., db.your-project.supabase.co)" false
prompt_var "port" "Database port (default: 5432)" false
prompt_var "dbname" "Database name (default: postgres)" false
prompt_var "user" "Database user (default: postgres)" false
prompt_var "password" "Database password" true

echo
echo "🤖 Databricks LLM Configuration"
echo "------------------------------"
prompt_var "DATABRICKS_TOKEN" "Databricks access token" true
prompt_var "DATABRICKS_BASE_URL" "Databricks workspace URL (e.g., https://dbc-xxx.cloud.databricks.com)" false
prompt_var "DATABRICKS_ENDPOINT" "Databricks endpoint path (default: /serving-endpoints/databricks-claude-sonnet-4/invocations)" false
prompt_var "DATABRICKS_MODEL_NAME" "Databricks model name (default: databricks-claude-sonnet-4)" false
prompt_var "DATABRICKS_TIMEOUT" "Request timeout in seconds (default: 60)" false

echo
echo "🦊 GitLab API Configuration"
echo "-------------------------"
prompt_var "GITLAB_API_TOKEN" "GitLab personal access token" true

# Set proper permissions
chmod 600 "$ENV_FILE"

echo
echo "✅ Environment file created: $ENV_FILE"

# Create or update GitLab runner configuration
echo
echo "🔧 GitLab Runner Configuration"
echo "-----------------------------"

if [[ $EUID -eq 0 ]]; then
    echo "Creating GitLab runner configuration template..."
    
    cat > "$CONFIG_FILE" << EOF
# GitLab Runner Configuration for Local AI Code Review
concurrent = 1
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "Local AI Code Reviewer Runner"
  url = "https://gitlab.com/"
  token = "RUNNER_TOKEN_TO_BE_REPLACED"
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
    env_file = ["$ENV_FILE"]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
EOF

    echo "✅ Configuration template created: $CONFIG_FILE"
    echo
    echo "📋 Next Steps:"
    echo "1. Register your GitLab runner:"
    echo "   sudo gitlab-runner register --config $CONFIG_FILE"
    echo
    echo "2. During registration, use these values:"
    echo "   - GitLab URL: https://gitlab.com"
    echo "   - Registration token: [Get from GitLab project Settings > CI/CD > Runners]"
    echo "   - Description: Local AI Code Reviewer Runner"
    echo "   - Tags: local-runner,ai-review"
    echo "   - Executor: docker"
    echo "   - Default image: python:3.9"
    echo
    echo "3. Restart GitLab runner:"
    echo "   sudo gitlab-runner restart"
    echo
    echo "4. Test configuration:"
    echo "   python3 check_local_runner.py"
    
else
    echo "⚠️  For system-wide GitLab runner configuration, please run this script with sudo"
    echo "Local environment file created at: $ENV_FILE"
    echo
    echo "To use with GitLab runner, you'll need to:"
    echo "1. Copy the environment variables to the system GitLab runner configuration"
    echo "2. Or run: sudo $(basename "$0")"
fi

echo
echo "🔐 Security Note:"
echo "The environment file contains sensitive information and has been set to read-only for the owner."
echo "Keep these credentials secure and never commit them to version control."
