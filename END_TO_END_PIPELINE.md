# End-to-End GitLab CI/CD Pipeline for SQL Code Review

## 🎯 Pipeline Overview

The GitLab CI/CD pipeline performs automated SQL code review on merge requests with the following stages:

## 📋 Stage 1: Precheck (`precheck-gitlab-env`)
**Purpose**: Validate GitLab CI environment and required variables
**File**: `gitlab_env_check.py`

**What it does**:
- ✅ Checks all required environment variables are set
- ✅ Validates GitLab API token format
- ✅ Ensures merge request context is available
- ✅ Installs basic dependencies

**Required Variables**:
- `CI_PROJECT_ID`
- `CI_MERGE_REQUEST_IID` 
- `GITLAB_API_TOKEN`
- Database connection vars: `host`, `port`, `dbname`, `user`, `password`
- AI integration: `DATABRICKS_TOKEN`, `DATABRICKS_BASE_URL`

## 🔌 Stage 2: Database Check (`precheck-database`)
**Purpose**: Early validation of Supabase cloud database connectivity
**File**: `test_supabase_connection.py`

**What it does**:
- ✅ Tests connection to Supabase using environment variables
- ✅ Validates read/write permissions with test table
- ✅ Provides clear error messages if connection fails
- ✅ Fails fast to save CI/CD minutes

**Benefits**:
- Catches database issues early before expensive setup steps
- Clear troubleshooting guidance for connection problems
- No waiting for PostgreSQL service startup (instant cloud connection)

## 🚀 Stage 3: SQL Code Review (`sql-code-review`)
**Purpose**: Full SQL analysis and review generation
**Files**: `cloud_db_setup.py` → `gitlab_ci_analyzer.py` → `main.py`

### 3.1 Database Setup (`cloud_db_setup.py`)
**What it does**:
1. ✅ **Test Connection**: Verify Supabase connectivity
2. ✅ **Create Schema**: Create `rules` table with vector column
3. ✅ **Load Rules**: Execute `database/insert_rules.sql` to populate SQL rules
4. ✅ **Vectorize Rules**: Run `rag/vectorize_rules.py` to generate CodeT5 embeddings

### 3.2 Changed File Analysis (`gitlab_ci_analyzer.py`)
**What it does**:
1. ✅ **Get Changed Files**: Identify modified `.sql` files in the merge request
2. ✅ **Extract Changed Lines**: Parse git diff to find added/modified lines
3. ✅ **Map to Statements**: Use `sqlparse` to map changed lines to complete SQL statements
4. ✅ **Analyze Statements**: Call `main.analyze_code_chunk()` for each changed statement

### 3.3 Code Review Generation (`main.py`)
**What it does**:
1. ✅ **Hybrid Retrieval**: Use regex + semantic search to find relevant rules
2. ✅ **AI Review**: Generate intelligent suggestions using Databricks Claude Sonnet 4
3. ✅ **Line Mapping**: Map issues back to correct line numbers in the original file
4. ✅ **JSON Output**: Create structured review results

### 3.4 GitLab Integration (`gitlab_ci_analyzer.py`)
**What it does**:
1. ✅ **Format Comments**: Convert review JSON to formatted GitLab comment
2. ✅ **Post to MR**: Use GitLab API to add review as merge request comment
3. ✅ **Artifacts**: Save `review_results.json` for later inspection

## 🔄 Data Flow

```
Merge Request Created
         ↓
┌─── Precheck Stage ───┐
│ gitlab_env_check.py  │ → Validate environment
└─────────────────────┘
         ↓
┌─── Database Check ───┐  
│test_supabase_conn.py│ → Test Supabase connection
└─────────────────────┘
         ↓
┌─── SQL Review Stage ─┐
│                      │
│ 1. cloud_db_setup.py │ → Setup database & vectorize rules
│         ↓            │
│ 2. gitlab_ci_analyzer│ → Find changed SQL files/lines
│         ↓            │  
│ 3. main.py          │ → Analyze each SQL statement
│         ↓            │
│ 4. GitLab API       │ → Post review comment
│                      │
└─────────────────────┘
         ↓
Review Comment Posted to MR
```

## 🧠 AI Analysis Process

For each changed SQL statement:

1. **Rule Retrieval** (`rag/retriever.py`):
   - Regex matching for pattern-based rules
   - Semantic search using CodeT5 embeddings
   - Hybrid scoring to find most relevant rules

2. **Review Generation** (`rag/generator.py`):
   - Send SQL code + relevant rules to Databricks Claude Sonnet 4
   - Generate intelligent, context-aware suggestions
   - Return structured JSON with line numbers and severity

3. **Line Mapping** (`utils/line_mapper.py`):
   - Map AI suggestions back to exact line numbers
   - Ensure suggestions reference correct file locations

## 📊 Output Format

**GitLab MR Comment**:
```markdown
## 🔍 SQL Code Review Results

Found **3 issues** in 2 changed SQL file(s):

### 📁 queries/user_report.sql
- **Line 15**: [HIGH] Use parameterized queries to prevent SQL injection
- **Line 23**: [MEDIUM] Consider adding index for better performance

### 📁 migrations/001_user_table.sql  
- **Line 8**: [LOW] Consider using more descriptive column names
```

**Artifacts** (`review_results.json`):
```json
{
  "total_issues": 3,
  "files_analyzed": ["queries/user_report.sql", "migrations/001_user_table.sql"],
  "issues": [
    {
      "file": "queries/user_report.sql",
      "line_number": 15,
      "severity": "HIGH", 
      "suggestion": "Use parameterized queries to prevent SQL injection",
      "code_snippet": "SELECT * FROM users WHERE id = " + user_id
    }
  ]
}
```

## 🔧 Troubleshooting

**Database Setup Fails**:
- Check Supabase credentials in GitLab CI/CD variables
- Verify `cloud_db_setup.py` can access `database/insert_rules.sql`
- Ensure `rag/vectorize_rules.py` can download CodeT5 model

**No Changed Files Detected**:
- Check git diff strategies in `gitlab_ci_analyzer.py`
- Verify merge request has actual SQL file changes
- Ensure target branch reference is correct

**AI Review Fails**:
- Verify `DATABRICKS_TOKEN` and `DATABRICKS_BASE_URL` are set
- Check network connectivity to Databricks API
- Review `rag/generator.py` error logs

## ✅ Success Indicators

- ✅ All 3 pipeline stages pass (green checkmarks)
- ✅ Review comment appears on merge request
- ✅ `review_results.json` artifact is generated
- ✅ Database has vectorized rules ready for future runs
- ✅ No manual intervention required

This end-to-end pipeline provides automated, intelligent SQL code review with cloud-scale reliability!
