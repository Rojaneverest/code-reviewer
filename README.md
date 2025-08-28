# AI Code Review Agent

This project is an AI Code Review Agent that uses a Retrieval-Augmented Generation (RAG) model to analyze SQL and PySpark code. It provides feedback based on a knowledge base of best practices stored in a PostgreSQL database and leverages LLM capabilities through Databricks for intelligent code review.

## 🚀 Local Runner Setup for GitLab CI/CD

This project can be configured to run on your local machine instead of GitLab's hosted runners, allowing direct access to your Databricks LLM endpoints.

### Quick Start for Local Runner

1. **Install GitLab Runner** (see [local-runner-setup.md](local-runner-setup.md) for detailed instructions)

2. **Configure Environment Variables:**
   ```bash
   sudo ./setup_local_runner_env.sh
   ```

3. **Register the Runner:**
   ```bash
   sudo gitlab-runner register
   ```
   - Tags: `local-runner,ai-review`
   - Executor: `docker`
   - Default image: `python:3.9`

4. **Test Configuration:**
   ```bash
   python3 check_local_runner.py
   ```

### Alternative: Docker Compose Setup

```bash
# Copy environment template
cp .env.runner.template .env.runner
# Edit .env.runner with your credentials
nano .env.runner

# Start GitLab runner in Docker
docker-compose -f docker-compose.runner.yml up -d

# Register the runner
docker-compose -f docker-compose.runner.yml exec gitlab-runner gitlab-runner register
```

## Project Structure

```
.Code-Review-Proj/
├── database/
│   ├── __init__.py
│   └── setup_db.py
├── rag/
│   ├── __init__.py
│   ├── generator.py
│   └── retriever.py
├── local-runner-setup.md          # Detailed local runner setup guide
├── setup_local_runner_env.sh      # Environment configuration script
├── check_local_runner.py          # Configuration validation script
├── docker-compose.runner.yml      # Docker-based runner setup
├── .env.runner.template           # Environment variables template
├── .gitlab-ci.yml                 # CI/CD pipeline (configured for local runner)
├── config.py
├── main.py
├── README.md
└── requirements.txt
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure PostgreSQL:**
   - Make sure you have PostgreSQL installed and running.
   - Create a database for this project.
   - Update `config.py` with your database credentials.

3. **Set up the database schema and initial data:**
   ```bash
   python database/setup_db.py
   ```

## Usage

To run the code review agent:

```bash
python main.py <path_to_code_file>
```
