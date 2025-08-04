# AI Code Review Agent

This project is an AI Code Review Agent that uses a Retrieval-Augmented Generation (RAG) model to analyze SQL and PySpark code. It provides feedback based on a knowledge base of best practices stored in a PostgreSQL database.

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
├── .gitignore
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
