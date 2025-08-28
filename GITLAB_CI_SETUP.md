# GitLab CI/CD Setup for SQL Code Review with Supabase

## 🎯 Overview
This setup enables automated SQL code review using a Supabase cloud database in GitLab CI/CD pipelines.

## 🔧 Configuration Changes Made

### 1. Migration from GitLab PostgreSQL Service to Supabase
- ❌ Removed unreliable GitLab PostgreSQL service
- ✅ Migrated to Supabase cloud database for better reliability  
- ✅ Added database connection precheck stage
- ✅ Improved pipeline failure detection

### 2. Environment Variables in GitLab CI/CD
**Required Variables** (set these in GitLab Project Settings → CI/CD → Variables):

#### Database Connection (Supabase)
```
host = db.ziuhftkruvdlwiyfepop.supabase.co
port = 5432
dbname = postgres
user = postgres
password = [your_supabase_password]  # Mark as Protected & Masked
```

#### AI Integration (Databricks)
```
DATABRICKS_TOKEN = [your_databricks_token]  # Mark as Protected & Masked
DATABRICKS_BASE_URL = [your_databricks_workspace_url]
```

#### GitLab Integration
```
GITLAB_TOKEN = [your_gitlab_personal_access_token]  # Mark as Protected & Masked
```

### 3. Database Configuration (config.py)
- ✅ Updated to read from environment variables
- ✅ Uses your variable naming convention
- ✅ Supports Supabase cloud database connection

### 4. Cloud Database Setup (cloud_db_setup.py)
- ✅ Connects to Supabase cloud database
- ✅ Uses existing `database/insert_rules.sql` for rule insertion  
- ✅ Runs `rag/vectorize_rules.py` to generate embeddings
- ✅ No waiting for PostgreSQL service (instant connection)
- ✅ Creates rules table with vector column for embeddings
- ✅ Handles both local model loading and HuggingFace downloads

### 5. Database Connection Precheck (test_supabase_connection.py)
- ✅ Early validation of Supabase database connectivity
- ✅ Provides clear error messages and troubleshooting tips
- ✅ Tests read/write permissions before main pipeline
- ✅ Fails fast to save CI/CD minutes

## 🚀 How It Works

1. **Merge Request Created** → GitLab triggers CI pipeline
2. **Precheck Stage** → Validates environment and installs dependencies
3. **Database Check Stage** → Tests Supabase connection (fails fast if issues)
4. **SQL Review Stage** → Sets up cloud database and analyzes SQL files

## 🔄 Key Changes from PostgreSQL Service Approach

| GitLab PostgreSQL Service | Supabase Cloud Database |
|---------------------------|-------------------------|
| `host = postgres` | `host = db.ziuhftkruvdlwiyfepop.supabase.co` |
| PostgreSQL service container | Supabase cloud database |
| Wait for service startup (60+ attempts) | Instant connection |
| Service reliability issues | ✅ Highly reliable cloud service |
| `setup_ci_database.py` | `cloud_db_setup.py` |
| No connection precheck | ✅ Early database validation |

## ✅ Next Steps

1. **Set GitLab CI/CD Variables**: Add the Supabase connection variables
2. **Test Database Connection**: Run `python test_supabase_connection.py` locally first
3. **Test Pipeline**: Create a test merge request with SQL changes
4. **Monitor**: Check pipeline logs for any issues

## 🐛 Troubleshooting

### Database Connection Issues
- **Connection Failed**: Verify Supabase credentials in GitLab CI/CD variables
- **Missing Variables**: Check that host, port, dbname, user, password are all set
- **Password Issues**: Ensure password is correct and marked as Protected & Masked
- **Network Issues**: Supabase should be accessible from GitLab CI runners

### Pipeline Issues  
- **Database Check Fails**: Check the database-check stage logs first
- **Token Issues**: Verify DATABRICKS_TOKEN and GITLAB_TOKEN formats
- **Model Download Issues**: First run may take longer as models download
- **Memory Issues**: CodeT5 model requires sufficient memory

## ⚡ Performance Benefits

- **Faster Startup**: No waiting for PostgreSQL service (saves 2-5 minutes per run)
- **More Reliable**: Cloud database eliminates service connectivity issues
- **Persistent Data**: Rules and vectors persist between pipeline runs
- **Early Failure Detection**: Database-check stage fails fast if connection issues
- **Better Monitoring**: Clear connection status and error messages

## 📁 Files Modified

- `.gitlab-ci.yml` - CI/CD pipeline configuration with vectorization support
- `config.py` - Database configuration with environment variables
- `gitlab_env_check.py` - Environment validation for your variable names
- `setup_ci_database.py` - PostgreSQL service initialization using `insert_rules.sql` and vectorization
- `rag/vectorize_rules.py` - Updated to work in CI environment with model fallbacks
- `test_env_vars.py` - Local testing with updated variable names
