# 🤖 Local AI Agent - Secure Local-First Architecture

A powerful, secure, local-first AI agent that bridges the gap between cloud AI and local system automation. This agent can interact with Git repositories, Docker containers, and your file system while maintaining complete security and privacy.

## 🎯 Key Features

- **🔐 Security First**: Multi-layered security with Bearer token authentication and strict CORS policies
- **🏠 Local-First**: All system operations happen on your machine, data never leaves unless explicitly sent to Gemini API
- **🧠 State-Aware AI**: Real-time system snapshot provides context to every AI decision
- **🛠️ Extensible Tools**: Easily add new automation capabilities
- **⚡ Async Architecture**: Non-blocking operations ensure responsive performance
- **🎨 Clean Separation**: Backend (FastAPI) + Frontend (React) architecture

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          Frontend (React - Port 3000)               │
│           User Interface & Chat                     │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS + Bearer Token
                   ▼
┌─────────────────────────────────────────────────────┐
│        Backend (FastAPI - Port 8000)                │
│    ┌─────────────────────────────────────────┐     │
│    │   AI Orchestrator (Gemini Integration)  │     │
│    └──────────┬───────────────────┬──────────┘     │
│               │                   │                 │
│    ┌──────────▼──────────┐  ┌────▼─────────┐      │
│    │  State Snapshot     │  │ Tool Executor│      │
│    │  (Git/Docker/FS)    │  │              │      │
│    └─────────────────────┘  └──────┬───────┘      │
│                                     │              │
│    ┌────────────────────────────────▼──────────┐  │
│    │         Protected Tool APIs               │  │
│    │  • Git Tools  • Docker Tools  • FS Tools │  │
│    └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │   Local System       │
         │  • Git Repos         │
         │  • Docker Daemon     │
         │  • File System       │
         └──────────────────────┘
```

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for frontend)
- **Docker** (optional, for Docker tools)
- **Git**
- **Gemini API Key** (get from https://ai.google.dev/)

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd /home/user/Jynco/local-ai-agent
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Setup Script

```bash
python setup.py
```

This will:
- Generate a secure authentication token
- Create your `.env` file
- Prompt for your Gemini API key
- Set your PROJECT_ROOT directory

### 5. Start the Backend

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Verify: Visit http://127.0.0.1:8000/docs to see the interactive API documentation.

### 6. Set Up Frontend

See [FRONTEND_SETUP.md](./FRONTEND_SETUP.md) for detailed instructions on creating the React frontend.

## 🔑 Configuration

Your `.env` file contains critical configuration:

```env
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Agent Security Token (auto-generated)
AGENT_SECRET_TOKEN=your_64_character_token_here

# Project Root - Defines the agent's operational sandbox
PROJECT_ROOT=/home/user/projects
```

### Environment Variables Explained

- **GEMINI_API_KEY**: Your Google Gemini API key for AI orchestration
- **AGENT_SECRET_TOKEN**: Bearer token for API authentication (keep secret!)
- **PROJECT_ROOT**: The top-level directory where the agent is allowed to operate

## 🛠️ Available Tools

### Git Tools

- **Get Git Status**: Check status of all repositories in PROJECT_ROOT
- **Clean Repository**: Remove all untracked files (DESTRUCTIVE - requires confirmation)
- **Commit Changes**: Stage and commit all changes with a message

### Docker Tools

- **List Containers**: View all Docker containers (running or all)
- **Start Container**: Start a stopped container

### File System Tools

- **List Directory**: Explore directory contents (sandboxed to PROJECT_ROOT)

## 🔒 Security Features

### Multi-Layer Security

1. **Bearer Token Authentication**: All tool endpoints require valid Bearer token
2. **Strict CORS**: Only whitelisted origins can access the API
3. **Directory Sandboxing**: File system access restricted to PROJECT_ROOT
4. **No Root Privileges**: Runs as regular user
5. **Tool Call Validation**: All tool calls are validated and logged

### Security Best Practices

- ✅ Never commit `.env` file to git (already in .gitignore)
- ✅ Use different tokens for dev/staging/production
- ✅ Rotate tokens regularly
- ✅ Keep PROJECT_ROOT narrow (don't use `/` or `C:\`)
- ✅ Review chat history regularly for suspicious requests

## 🧪 Testing the Agent

### Test Basic Functionality

1. **Start the backend** (see Quick Start)

2. **Test Health Endpoint**:
   ```bash
   curl http://localhost:8000/
   ```

3. **Test Protected Endpoint** (should fail without token):
   ```bash
   curl http://localhost:8000/api/tools/git/status
   ```

4. **Test with Token**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        http://localhost:8000/api/tools/git/status
   ```

### Example Prompts

Once the full system is running, try:

- "What's the status of my Git repositories?"
- "List all my Docker containers"
- "Are any of my repos dirty?"
- "Start the container named my-app"
- "Show me what's in /home/user/projects"

## 📁 Project Structure

```
local-ai-agent/
├── .env                    # Your secrets (DO NOT COMMIT)
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
├── main.py                 # FastAPI application & orchestrator
├── security.py             # Authentication logic
├── setup.py                # Setup script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── FRONTEND_SETUP.md       # Frontend setup guide
├── tools/
│   ├── __init__.py
│   ├── git_tools.py        # Git automation
│   ├── docker_tools.py     # Docker automation
│   └── fs_tools.py         # File system operations
└── frontend/               # React frontend (create separately)
    └── (see FRONTEND_SETUP.md)
```

## 🎨 Customization

### Adding New Tools

1. **Create tool module** in `tools/my_new_tool.py`:
   ```python
   async def my_new_function(param: str):
       def blocking_operation():
           # Your logic here
           return {"result": "success"}
       return await asyncio.to_thread(blocking_operation)
   ```

2. **Add FunctionDeclaration** in `main.py`:
   ```python
   my_tool_func = FunctionDeclaration(
       name="my_new_function",
       description="Clear description of what this tool does",
       parameters={...}
   )
   ```

3. **Add to agent_tools** Tool object

4. **Create API endpoint**:
   ```python
   @app.post("/api/tools/my/endpoint", dependencies=[Depends(verify_token)])
   async def my_endpoint(request: MyRequest):
       return await my_new_tool.my_new_function(request.param)
   ```

5. **Update execute_tool** mapping

## 🔧 Troubleshooting

### Backend won't start

- Check that your virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure .env file exists with valid keys

### "AGENT_SECRET_TOKEN not found" error

- Run `python setup.py` to create .env file
- Or manually create .env from .env.example

### Gemini API errors

- Verify your GEMINI_API_KEY is correct
- Check you have API access enabled at https://ai.google.dev/
- Ensure you haven't exceeded rate limits

### CORS errors in frontend

- Verify frontend is running on http://localhost:3000
- Check CORS whitelist in main.py matches your frontend URL
- Ensure you're including the Authorization header

### Docker tools not working

- Ensure Docker daemon is running
- Verify Docker is accessible without sudo (on Linux)
- Check Docker socket permissions

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Frontend Setup Guide](./FRONTEND_SETUP.md)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)

## 🤝 Contributing

This is a template architecture - feel free to extend and customize for your needs!

Ideas for extensions:
- Add more tools (AWS, Azure, Kubernetes, etc.)
- Implement persistent chat history (SQLite, PostgreSQL)
- Add multi-user support
- Integrate local LLMs via Ollama
- Create mobile frontend
- Add voice interface

## 📄 License

[Specify your license here]

## 🙏 Acknowledgments

Built on the shoulders of giants:
- FastAPI by Sebastián Ramírez
- Google Gemini API
- GitPython, Docker SDK, and the Python community

---

**Remember**: This agent has powerful capabilities. Always review what it's doing, especially for destructive operations like `git clean`. The AI is a tool to amplify your productivity, not replace your judgment.

**Happy Automating!** 🚀
