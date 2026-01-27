# Quickstart: Project Setup

**Feature**: 001-project-setup
**Time to Complete**: ~15 minutes

## Prerequisites

- Python 3.11 or higher installed
- Git installed
- Access to a Neon PostgreSQL database instance
- OpenAI API key (for future features)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd todo-ai-chatbot
```

## Step 2: Create Python Virtual Environment

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows (PowerShell)**:
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**:
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS**:
```bash
source .venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
DATABASE_URL=postgresql://username:password@your-neon-host.neon.tech/dbname?sslmode=require
OPENAI_API_KEY=sk-your-openai-api-key
```

**Important**: Never commit the `.env` file to version control.

## Step 5: Start the Development Server

```bash
uvicorn src.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database connected successfully
INFO:     Application startup complete.
```

## Step 6: Verify Health Check

Open a browser or use curl to check the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "server": "running",
  "database": "connected",
  "timestamp": "2026-01-19T12:00:00Z"
}
```

## Troubleshooting

### Database Connection Failed

If you see `"database": "disconnected"`:

1. Verify your DATABASE_URL is correct
2. Check that your Neon database is active (not suspended)
3. Ensure SSL mode is enabled: `?sslmode=require`
4. Verify network connectivity to Neon servers

### Missing Environment Variables

If the server fails to start with "DATABASE_URL not found":

1. Ensure `.env` file exists in the `backend/` directory
2. Check that the variable names match exactly (case-sensitive)
3. Restart the server after changing `.env`

### Python Version Issues

If you see syntax errors or import failures:

1. Verify Python version: `python --version` (must be 3.11+)
2. Ensure you're using the virtual environment (check prompt prefix)

## Next Steps

After successful setup, you can:

1. Run tests: `pytest`
2. View API docs: Open http://localhost:8000/docs
3. Proceed to implementing database models and MCP tools

## Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] `.env` file configured with valid credentials
- [ ] Server starts without errors
- [ ] Health check returns `"status": "healthy"`
- [ ] Database shows `"database": "connected"`
