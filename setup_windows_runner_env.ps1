# PowerShell script for setting up GitLab Runner environment variables on Windows
# Run this script as Administrator to configure environment variables for the GitLab Runner

param(
    [string]$ConfigPath = "C:\GitLab-Runner\config.toml"
)

Write-Host "🚀 GitLab Runner Windows Environment Setup" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Function to prompt for environment variable
function Prompt-EnvVar {
    param(
        [string]$VarName,
        [string]$Description,
        [bool]$IsSecret = $false
    )
    
    $currentValue = [Environment]::GetEnvironmentVariable($VarName, "Machine")
    if ($currentValue) {
        if ($IsSecret) {
            $displayValue = "[HIDDEN - already set]"
        } else {
            $displayValue = $currentValue
        }
        Write-Host "Current value for $VarName`: $displayValue" -ForegroundColor Yellow
    }
    
    if ($IsSecret) {
        $value = Read-Host -Prompt "$Description" -AsSecureString
        $value = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($value))
    } else {
        $value = Read-Host -Prompt "$Description"
    }
    
    if ($value) {
        [Environment]::SetEnvironmentVariable($VarName, $value, "Machine")
        Write-Host "✅ Set $VarName" -ForegroundColor Green
    }
}

Write-Host
Write-Host "🗄️  Database Configuration (Local PostgreSQL)" -ForegroundColor Cyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan
Prompt-EnvVar "host" "Database host (default: localhost)" 
Prompt-EnvVar "port" "Database port (default: 5432)"
Prompt-EnvVar "dbname" "Database name (default: rules)"
Prompt-EnvVar "user" "Database user (default: postgres)"
Prompt-EnvVar "password" "Database password (default: root)" $true

Write-Host
Write-Host "🤖 Databricks LLM Configuration" -ForegroundColor Cyan
Write-Host "------------------------------" -ForegroundColor Cyan
Prompt-EnvVar "DATABRICKS_TOKEN" "Databricks access token" $true
Prompt-EnvVar "DATABRICKS_BASE_URL" "Databricks workspace URL (e.g., https://dbc-xxx.cloud.databricks.com)"
Prompt-EnvVar "DATABRICKS_ENDPOINT" "Databricks endpoint path (default: /serving-endpoints/databricks-claude-sonnet-4/invocations)"
Prompt-EnvVar "DATABRICKS_MODEL_NAME" "Databricks model name (default: databricks-claude-sonnet-4)"
Prompt-EnvVar "DATABRICKS_TIMEOUT" "Request timeout in seconds (default: 60)"

Write-Host
Write-Host "🦊 GitLab API Configuration" -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan
Prompt-EnvVar "GITLAB_API_TOKEN" "GitLab personal access token" $true

Write-Host
Write-Host "✅ Environment variables configured!" -ForegroundColor Green

# Check if GitLab Runner service needs restart
Write-Host
Write-Host "🔧 GitLab Runner Service" -ForegroundColor Cyan
Write-Host "----------------------" -ForegroundColor Cyan

$service = Get-Service -Name "gitlab-runner" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "GitLab Runner service found. Restarting to apply new environment variables..." -ForegroundColor Yellow
    Restart-Service -Name "gitlab-runner"
    Write-Host "✅ GitLab Runner service restarted" -ForegroundColor Green
} else {
    Write-Host "⚠️  GitLab Runner service not found. Make sure it's installed and running." -ForegroundColor Yellow
}

Write-Host
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test configuration: python check_local_runner.py" -ForegroundColor White
Write-Host "2. Create a test merge request with SQL changes" -ForegroundColor White
Write-Host "3. Verify the pipeline runs on your local runner" -ForegroundColor White

Write-Host
Write-Host "🔐 Security Note:" -ForegroundColor Yellow
Write-Host "Environment variables are stored at the machine level and accessible to the GitLab Runner service." -ForegroundColor White
Write-Host "Keep these credentials secure and never commit them to version control." -ForegroundColor White
