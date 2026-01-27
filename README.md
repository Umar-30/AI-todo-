 # Todo AI Chatbot                                                                                                                                   
  AI-powered Todo Chatbot with voice support, real-time task management, and MCP-compliant architecture.                                           
  
  ## Tech Stack

  ### Backend
  - **Framework:** FastAPI
  - **Database:** PostgreSQL (Neon)
  - **ORM:** SQLModel
  - **AI:** OpenRouter API (GPT-4o-mini)
  - **Auth:** JWT + bcrypt

  ### Frontend
  - **Framework:** React 18 + TypeScript
  - **Build Tool:** Vite
  - **UI:** ChatKit React
  - **Routing:** React Router v7
  - **Auth:** Better Auth

  ## Prerequisites

  - Python 3.11+
  - Node.js 18+
  - PostgreSQL (Neon recommended)
  - OpenRouter API Key

  ## Project Structure

  Todo AI Chatbot/
  ├── backend/           # FastAPI backend
  │   ├── src/
  │   │   ├── api/       # REST endpoints
  │   │   ├── agent/     # AI task agent
  │   │   ├── models/    # SQLModel models
  │   │   ├── mcp/       # MCP server & tools
  │   │   └── main.py    # App entry point
  │   ├── .env           # Environment variables
  │   └── requirements.txt
  ├── frontend/          # React frontend
  │   ├── src/
  │   │   ├── components/
  │   │   ├── hooks/
  │   │   ├── pages/
  │   │   └── services/
  │   └── package.json
  └── README.md

  ## Setup & Installation

  ### 1. Clone Repository

  ```bash
  git clone <repository-url>
  cd "Todo AI Chatbot"

  2. Backend Setup

  # Navigate to backend
  cd backend

  # Create virtual environment
  python -m venv .venv

  # Activate virtual environment
  # Windows:
  .venv\Scripts\activate
  # Linux/Mac:
  source .venv/bin/activate

  # Install dependencies
  pip install -r requirements.txt
  # OR using uv (faster)
  uv pip install -r requirements.txt

  3. Backend Environment Variables

  Create backend/.env file:

  # Database (Neon PostgreSQL)
  DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

  # OpenRouter AI
  OPENROUTE_API_KEY=sk-or-v1-xxxxx
  OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
  OPENROUTER_MODEL=openai/gpt-4o-mini

  # Environment
  ENVIRONMENT=development

  4. Frontend Setup

  # Navigate to frontend
  cd frontend

  # Install dependencies
  npm install

  Running the Application

  Start Backend Server

  cd backend

  # Activate virtual environment (if not already)
  # Windows:
  .venv\Scripts\activate
  # Linux/Mac:
  source .venv/bin/activate

  # Run server
  uvicorn src.main:app --reload --port 8000

  Backend runs at: http://localhost:8000

  Start Frontend Dev Server

  cd frontend

  # Run development server
  npm run dev

  Frontend runs at: http://localhost:5173

  Available Commands

  Backend Commands
  ┌─────────────────────────────────────────────────┬──────────────────────────────────┐
  │                     Command                     │           Description            │
  ├─────────────────────────────────────────────────┼──────────────────────────────────┤
  │ uvicorn src.main:app --reload                   │ Start dev server with hot reload │
  ├─────────────────────────────────────────────────┼──────────────────────────────────┤
  │ uvicorn src.main:app --host 0.0.0.0 --port 8000 │ Start production server          │
  ├─────────────────────────────────────────────────┼──────────────────────────────────┤
  │ pytest                                          │ Run tests                        │
  ├─────────────────────────────────────────────────┼──────────────────────────────────┤
  │ pip install -r requirements.txt                 │ Install dependencies             │
  └─────────────────────────────────────────────────┴──────────────────────────────────┘
  Frontend Commands
  ┌─────────────────┬──────────────────────────┐
  │     Command     │       Description        │
  ├─────────────────┼──────────────────────────┤
  │ npm run dev     │ Start development server │
  ├─────────────────┼──────────────────────────┤
  │ npm run build   │ Build for production     │
  ├─────────────────┼──────────────────────────┤
  │ npm run preview │ Preview production build │
  ├─────────────────┼──────────────────────────┤
  │ npm install     │ Install dependencies     │
  └─────────────────┴──────────────────────────┘
  API Endpoints
  ┌────────┬───────────────────┬──────────────────────────────┐
  │ Method │     Endpoint      │         Description          │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ GET    │ /health           │ Health check                 │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ POST   │ /api/auth/signup  │ User registration            │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ POST   │ /api/auth/login   │ User login                   │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ GET    │ /api/tasks        │ List all tasks               │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ POST   │ /api/tasks        │ Create task                  │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ PATCH  │ /api/tasks/{id}   │ Update task                  │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ DELETE │ /api/tasks/{id}   │ Delete task                  │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ POST   │ /api/chat         │ Chat with AI                 │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ POST   │ /api/voice        │ Voice input                  │
  ├────────┼───────────────────┼──────────────────────────────┤
  │ GET    │ /api/tasks/stream │ Real-time task updates (SSE) │
  └────────┴───────────────────┴──────────────────────────────┘
  Deployment

  Hugging Face Spaces (Backend)

  The backend is deployed at: https://huggingface.co/spaces/umar-30/AI-todo

  Set these secrets in HF Space settings:
  - DATABASE_URL
  - OPENROUTE_API_KEY

  Frontend Deployment

  cd frontend
  npm run build
  # Deploy dist/ folder to Vercel, Netlify, etc.

  Features

  - Task CRUD operations
  - AI-powered chat interface
  - Voice input/output (STT/TTS)
  - Real-time task updates (SSE)
  - JWT Authentication
  - User registration & login

  License

  MIT
