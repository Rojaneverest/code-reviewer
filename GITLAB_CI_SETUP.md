# GitLab CI/CD Setup for SQL Code Review

## 🎯 Overview
This setup enables automated SQL code review using PostgreSQL service in GitLab CI/CD pipelines.

## 🔧 Configuration Changes Made

### 1. GitLab CI Pipeline (.gitlab-ci.yml)
- ✅ Added PostgreSQL 13 service
- ✅ Configured PostgreSQL environment variables
- ✅ Added database initialization step
- ✅ Updated variable references to match your naming convention

### 2. Environment Variables in GitLab CI/CD
**Required Variables** (set these in GitLab Project Settings → CI/CD → Variables):

```
DATABRICKS_TOKEN = abc
GITLAB_API_TOKEN = cde
dbname = rules
user = postgres
password = root
host = postgres  # Note: Use 'postgres' for GitLab CI service
port = 5432
```

### 3. Database Configuration (config.py)
- ✅ Updated to read from environment variables
- ✅ Uses your variable naming convention
- ✅ Maintains localhost fallback for local development

### 4. CI Database Setup (setup_ci_database.py)
- ✅ Uses existing `database/insert_rules.sql` for rule insertion
- ✅ Runs `rag/vectorize_rules.py` to generate embeddings
- ✅ Waits for PostgreSQL to be ready
- ✅ Creates rules table with vector column for embeddings
- ✅ Uses your variable naming convention
- ✅ Handles both local model loading and HuggingFace downloads

### 5. Environment Validation (gitlab_env_check.py)
- ✅ Updated to check your variable names
- ✅ Validates PostgreSQL service connectivity
- ✅ Provides clear error messages and setup instructions

## 🚀 How It Works

1. **Merge Request Created** → GitLab triggers CI pipeline
2. **Precheck Stage** → Validates all environment variables
3. **PostgreSQL Service** → Starts automatically 
4. **Database Setup** → Loads rules from `database/insert_rules.sql`
5. **Rule Vectorization** → Runs `rag/vectorize_rules.py` to generate embeddings
6. **SQL Review Stage** → Analyzes changed SQL files and posts comments

## 🔄 Key Changes from Local Setup

| Local Development | GitLab CI |
|-------------------|-----------|
| `host = localhost` | `host = postgres` |
| Local PostgreSQL instance | PostgreSQL service container |
| Manual database setup | Automated via `setup_ci_database.py` |
| Local model files | Uses existing models/ folder or downloads from HuggingFace |
| Manual rule vectorization | Automated via `rag/vectorize_rules.py` |

## ✅ Next Steps

1. **Set GitLab CI/CD Variables**: Add the required variables in your GitLab project
2. **Test Pipeline**: Create a test merge request with SQL changes
3. **Monitor**: Check pipeline logs for any issues

## 🐛 Troubleshooting

- **Database Connection Failed**: Ensure `host=postgres` in GitLab CI variables
- **Missing Variables**: Check environment validation in precheck stage
- **Token Issues**: Verify DATABRICKS_TOKEN and GITLAB_API_TOKEN formats
- **Model Download Issues**: First run may take longer as models download from HuggingFace
- **Memory Issues**: CodeT5 model requires sufficient memory; consider using smaller models for CI

## ⚡ Performance Notes

- **First Run**: May take 5-10 minutes as it downloads CodeT5 model (~200MB)
- **Subsequent Runs**: Faster as model is cached
- **Model Location**: Uses local `models/codet5p-220m/` if available, otherwise downloads
- **Memory Usage**: CodeT5 requires ~500MB RAM for embeddings generation

## 📁 Files Modified

- `.gitlab-ci.yml` - CI/CD pipeline configuration with vectorization support
- `config.py` - Database configuration with environment variables
- `gitlab_env_check.py` - Environment validation for your variable names
- `setup_ci_database.py` - PostgreSQL service initialization using `insert_rules.sql` and vectorization
- `rag/vectorize_rules.py` - Updated to work in CI environment with model fallbacks
- `test_env_vars.py` - Local testing with updated variable names
