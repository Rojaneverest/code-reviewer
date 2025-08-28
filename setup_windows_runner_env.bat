@echo off
REM Batch script for setting up GitLab Runner environment variables on Windows
REM Run this script as Administrator

echo 🚀 GitLab Runner Windows Environment Setup
echo =========================================

echo.
echo 🗄️  Database Configuration (Local PostgreSQL)
echo --------------------------------------------
set /p host="Database host (default: localhost): "
if "%host%"=="" set host=localhost
setx host "%host%" /M

set /p port="Database port (default: 5432): "
if "%port%"=="" set port=5432
setx port "%port%" /M

set /p dbname="Database name (default: rules): "
if "%dbname%"=="" set dbname=rules
setx dbname "%dbname%" /M

set /p user="Database user (default: postgres): "
if "%user%"=="" set user=postgres
setx user "%user%" /M

set /p password="Database password (default: root): "
if "%password%"=="" set password=root
setx password "%password%" /M

echo.
echo 🤖 Databricks LLM Configuration
echo ------------------------------
set /p DATABRICKS_TOKEN="Databricks access token: "
if not "%DATABRICKS_TOKEN%"=="" setx DATABRICKS_TOKEN "%DATABRICKS_TOKEN%" /M

set /p DATABRICKS_BASE_URL="Databricks workspace URL: "
if not "%DATABRICKS_BASE_URL%"=="" setx DATABRICKS_BASE_URL "%DATABRICKS_BASE_URL%" /M

set /p DATABRICKS_ENDPOINT="Databricks endpoint (default: /serving-endpoints/databricks-claude-sonnet-4/invocations): "
if not "%DATABRICKS_ENDPOINT%"=="" setx DATABRICKS_ENDPOINT "%DATABRICKS_ENDPOINT%" /M

set /p DATABRICKS_MODEL_NAME="Databricks model name (default: databricks-claude-sonnet-4): "
if not "%DATABRICKS_MODEL_NAME%"=="" setx DATABRICKS_MODEL_NAME "%DATABRICKS_MODEL_NAME%" /M

set /p DATABRICKS_TIMEOUT="Request timeout in seconds (default: 60): "
if not "%DATABRICKS_TIMEOUT%"=="" setx DATABRICKS_TIMEOUT "%DATABRICKS_TIMEOUT%" /M

echo.
echo 🦊 GitLab API Configuration
echo -------------------------
set /p GITLAB_API_TOKEN="GitLab personal access token: "
if not "%GITLAB_API_TOKEN%"=="" setx GITLAB_API_TOKEN "%GITLAB_API_TOKEN%" /M

echo.
echo ✅ Environment variables configured!

echo.
echo 🔧 Restarting GitLab Runner service...
net stop gitlab-runner
net start gitlab-runner

echo.
echo 📋 Next Steps:
echo 1. Test configuration: python check_local_runner.py
echo 2. Create a test merge request with SQL changes
echo 3. Verify the pipeline runs on your local runner

echo.
echo 🔐 Security Note:
echo Environment variables are stored at the machine level.
echo Keep these credentials secure and never commit them to version control.

pause
