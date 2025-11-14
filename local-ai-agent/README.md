# Secure Local-First AI Agent

A production-ready, secure AI agent that solves the "Cloud-to-Local Bridge" challenge by enabling safe interaction between cloud-based AI services and your local development environment.

## 🎯 Overview

This project implements a sophisticated two-component architecture:

1. **Frontend (React)**: A sleek web UI served on `localhost:3000` that acts as your command center
2. **Backend (FastAPI)**: A powerful Python server on `localhost:8000` that orchestrates tasks and communicates with Google Gemini

### Key Features

- ✅ **State-Aware AI**: Automatically gathers real-time system context before every request
- ✅ **Multi-Layer Security**: Bearer token authentication + strict CORS policies
- ✅ **Async Operations**: Non-blocking I/O for maximum performance
- ✅ **Extensible Tools**: Easily add new automation capabilities
- ✅ **Future-Proof**: Architecture ready for local LLM integration (Ollama, etc.)

### Current Capabilities

- 🔧 **Git Automation**: Check repository status, commit changes, clean repos
- 🐳 **Docker Management**: List and start containers
- 📁 **Filesystem Operations**: Sandboxed directory exploration
- 💬 **Natural Language Interface**: Converse with your local environment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+ and npm
- Git
- Docker (optional, for Docker tools)
- A Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd /home/user/local-ai-agent
   ```

2. **Set up the backend**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Copy the example and edit with your keys
   cp .env.example .env
   nano .env  # or use your preferred editor
   ```
   
   Update these critical values in `.env`:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `AGENT_SECRET_TOKEN`: Already generated (or regenerate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `PROJECT_ROOT`: The directory where your projects live (e.g., `/home/user/projects`)

4. **Set up the frontend**:
   ```bash
   cd frontend
   
   # Copy frontend environment file
   cp .env .env.local  # Already configured with matching token
   
   # Install dependencies
   npm install
   ```

### Running the System

You need **two terminal windows**:

**Terminal 1 - Backend**:
```bash
cd /home/user/local-ai-agent
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend**:
```bash
cd /home/user/local-ai-agent/frontend
npm start
```

The frontend will automatically open at `http://localhost:3000`.

## 📖 Usage Examples

Once both servers are running, try these prompts:

### Simple Conversation
```
You: Hello, can you help me?
Agent: Hello! I'm your local AI assistant. I can help you...
```

### Git Operations
```
You: Check the status of all my git repositories
Agent: [Scans PROJECT_ROOT and reports status of each repo]

You: Commit all changes in /home/user/projects/myapp with message "Fix bug"
Agent: [Stages and commits changes]
```

### Docker Management
```
You: List all my Docker containers
Agent: [Shows running and stopped containers]

You: Start the container named "postgres-db"
Agent: [Starts the container if it's stopped]
```

### State Awareness
```
You: Start my database container
Agent: I checked your containers - the "postgres-db" container is already running!
```

## 🔒 Security Features

### Multi-Layer Protection

1. **Bearer Token Authentication**: Every API endpoint requires a secret token
2. **Strict CORS**: Only `localhost:3000` can communicate with the backend
3. **Filesystem Sandboxing**: File operations are restricted to `PROJECT_ROOT`
4. **No Cloud Backdoors**: The cloud never "reaches into" your machine
5. **Environment Isolation**: All secrets stored in `.env` files (never committed)

### Architecture Diagram

```
┌─────────────────────────────────────┐
│    Frontend (localhost:3000)         │
│    User Interface (Sandboxed)        │
└──────────────┬──────────────────────┘
               │ HTTPS + Bearer Token
               ▼
┌─────────────────────────────────────┐
│   Backend (localhost:8000)           │
│   ├─ Tool Executors (Git, Docker)   │
│   ├─ Security Layer                  │
│   └─ AI Orchestrator                 │
└──────────────┬──────────────────────┘
               │ Outbound Only
               ▼
┌─────────────────────────────────────┐
│   Google Gemini API                  │
│   (Intelligence Layer)               │
└─────────────────────────────────────┘
```

## 🛠️ Development

### Project Structure

```
local-ai-agent/
├── main.py                    # FastAPI app + AI Orchestrator
├── security.py                # Bearer token authentication
├── tools/                     # Automation capabilities
│   ├── git_tools.py          # Git operations
│   ├── docker_tools.py       # Docker management
│   └── fs_tools.py           # Filesystem tools
├── frontend/                  # React application
│   ├── src/
│   │   ├── api.ts            # Secure API client
│   │   ├── Chat.tsx          # Chat interface
│   │   └── App.tsx           # Main app component
│   └── package.json
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md
```

### Adding New Tools

1. **Create the tool function** in `tools/new_tool.py`:
   ```python
   async def my_new_tool(param: str):
       def blocking_operation():
           # Your tool logic here
           return {"result": "success"}
       return await asyncio.to_thread(blocking_operation)
   ```

2. **Define the API endpoint** in `main.py`:
   ```python
   @app.post("/api/tools/newtool", dependencies=[Depends(verify_token)])
   async def new_tool_api(param: str):
       return await new_tool.my_new_tool(param)
   ```

3. **Register with Gemini** in `main.py`:
   ```python
   new_tool_func = FunctionDeclaration(
       name="my_new_tool",
       description="Clear description of what this tool does",
       parameters={"type": "object", "properties": {...}}
   )
   ```

4. **Update the tool executor** mapping in `execute_tool()`:
   ```python
   url_map = {
       ...
       "my_new_tool": {"method": "POST", "url": "/api/tools/newtool"},
   }
   ```

## 🔮 Future Roadmap

- [ ] Local LLM integration (Ollama)
- [ ] Conversation persistence (SQLite)
- [ ] Multi-user support
- [ ] Additional tools (AWS, Azure, Ansible, etc.)
- [ ] WebSocket for streaming responses
- [ ] Voice interface
- [ ] Mobile app

## 📝 Environment Variables Reference

### Backend (.env)
```bash
GEMINI_API_KEY=your_api_key_here
AGENT_SECRET_TOKEN=64_character_hex_token
PROJECT_ROOT=/home/user/projects
```

### Frontend (frontend/.env)
```bash
REACT_APP_AGENT_API_KEY=same_64_character_hex_token_as_backend
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check `.env` file exists and contains all required variables

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check that `REACT_APP_AGENT_API_KEY` matches `AGENT_SECRET_TOKEN`
- Open browser console (F12) for detailed error messages

### "Invalid token" errors
- Ensure tokens match exactly between backend/.env and frontend/.env
- Tokens must be 64 hex characters (no spaces or quotes)

### Docker tools not working
- Verify Docker daemon is running: `docker ps`
- Check Docker permissions (may need to add user to docker group)

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- UI framework: [React](https://react.dev/)

## 📧 Support

For issues and questions, please open an issue in the GitHub repository.

---

**Built with ❤️ for developers who value security, privacy, and local-first computing.**
