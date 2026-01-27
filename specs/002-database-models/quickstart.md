# Quickstart: Database Models

**Feature**: 002-database-models
**Time to Complete**: ~10 minutes

## Prerequisites

- Completed 001-project-setup (backend running with database connection)
- Python virtual environment activated
- `.env` file configured with valid DATABASE_URL

## Step 1: Verify Base Setup

Ensure the backend from 001-project-setup is working:

```bash
cd backend
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate on Windows

uvicorn src.main:app --reload
```

Verify health check returns `"database": "connected"`:
```bash
curl http://localhost:8000/health
```

## Step 2: Create Tables

After implementing the models, tables are created automatically on server startup. The `create_tables()` function in `database.py` runs during the application lifespan.

Restart the server to trigger table creation:
```bash
# Stop the server (Ctrl+C) and restart
uvicorn src.main:app --reload
```

Look for log output:
```
INFO: Database tables created successfully
```

## Step 3: Verify Tables in Database

Connect to your Neon database and verify tables exist:

**Option A: Using psql**
```bash
psql $DATABASE_URL -c "\dt"
```

Expected output:
```
           List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+----------
 public | conversations | table | neondb_owner
 public | messages      | table | neondb_owner
 public | tasks         | table | neondb_owner
```

**Option B: Using Neon Console**
1. Go to https://console.neon.tech
2. Select your project
3. Navigate to Tables tab
4. Verify `tasks`, `conversations`, `messages` tables exist

## Step 4: Test CRUD Operations

Use Python REPL to test basic operations:

```bash
cd backend
python -c "
from src.database import get_engine, create_tables
from src.models import Task, Conversation, Message
from sqlmodel import Session
from uuid import uuid4
from datetime import datetime, timezone

# Create tables if not exists
create_tables()

engine = get_engine()

# Test Task CRUD
with Session(engine) as session:
    # Create
    task = Task(
        user_id='test-user',
        title='Test Task',
        description='A test task'
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    print(f'Created task: {task.id}')

    # Read
    task = session.get(Task, task.id)
    print(f'Read task: {task.title}')

    # Update
    task.completed = True
    session.add(task)
    session.commit()
    print(f'Updated task completed: {task.completed}')

    # Delete
    session.delete(task)
    session.commit()
    print('Deleted task')

print('Task CRUD test passed!')
"
```

## Step 5: Test Relationships

Test Conversation → Message cascade delete:

```bash
python -c "
from src.database import get_engine
from src.models import Conversation, Message
from sqlmodel import Session, select

engine = get_engine()

with Session(engine) as session:
    # Create conversation with messages
    conv = Conversation(user_id='test-user')
    session.add(conv)
    session.commit()
    session.refresh(conv)

    msg1 = Message(
        user_id='test-user',
        conversation_id=conv.id,
        role='user',
        content='Hello'
    )
    msg2 = Message(
        user_id='test-user',
        conversation_id=conv.id,
        role='assistant',
        content='Hi there!'
    )
    session.add_all([msg1, msg2])
    session.commit()

    print(f'Created conversation {conv.id} with 2 messages')

    # Verify messages exist
    messages = session.exec(
        select(Message).where(Message.conversation_id == conv.id)
    ).all()
    print(f'Messages before delete: {len(messages)}')

    # Delete conversation (should cascade to messages)
    session.delete(conv)
    session.commit()

    # Verify messages deleted
    messages = session.exec(
        select(Message).where(Message.conversation_id == conv.id)
    ).all()
    print(f'Messages after delete: {len(messages)}')

print('Cascade delete test passed!')
"
```

## Troubleshooting

### Tables Not Created

If tables don't appear:
1. Check database connection: `curl http://localhost:8000/health`
2. Verify DATABASE_URL in `.env`
3. Check server logs for errors
4. Manually call `create_tables()`:
   ```python
   from src.database import create_tables
   create_tables()
   ```

### Foreign Key Errors

If you see foreign key constraint errors:
1. Ensure Conversation exists before creating Messages
2. Check conversation_id is valid UUID
3. Verify cascade delete is configured

### Import Errors

If models fail to import:
1. Ensure `backend/src/models/__init__.py` exists
2. Check all model files have correct imports
3. Verify SQLModel is installed: `pip install sqlmodel`

## Verification Checklist

- [ ] Server starts without errors
- [ ] Three tables created (tasks, conversations, messages)
- [ ] Task CRUD operations work
- [ ] Conversation CRUD operations work
- [ ] Message CRUD operations work
- [ ] Cascade delete works (deleting conversation removes messages)
- [ ] Timestamps auto-populate on create/update
