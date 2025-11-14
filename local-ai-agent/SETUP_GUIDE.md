# Detailed Setup Guide

This guide walks you through setting up the Secure Local-First AI Agent step by step.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Configuration](#frontend-configuration)
5. [Testing the Installation](#testing-the-installation)
6. [Common Issues](#common-issues)

## System Requirements

### Required Software

- **Python 3.11 or higher**
  - Check: `python3 --version`
  - Install: Visit [python.org](https://www.python.org/downloads/)

- **Node.js 16+ and npm**
  - Check: `node --version && npm --version`
  - Install: Visit [nodejs.org](https://nodejs.org/)

- **Git**
  - Check: `git --version`
  - Usually pre-installed on Linux/Mac, download from [git-scm.com](https://git-scm.com/) for Windows

- **Docker** (Optional, for Docker tools)
  - Check: `docker --version`
  - Install: Visit [docker.com](https://www.docker.com/)

### Required API Keys

- **Google Gemini API Key**
  - Free tier available
  - Get one at: https://aistudio.google.com/app/apikey
  - Click "Create API Key" and save it securely

## Initial Setup

### Step 1: Navigate to Project Directory

```bash
cd /home/user/local-ai-agent
```

### Step 2: Verify Project Structure

Ensure you have these files:
```
local-ai-agent/
├── main.py
├── security.py
├── tools/
│   ├── __init__.py
│   ├── git_tools.py
│   ├── docker_tools.py
│   └── fs_tools.py
├── requirements.txt
├── .env.example
├── .gitignore
└── frontend/
```

## Backend Configuration

### Step 1: Create Python Virtual Environment

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (Linux/Mac/Git Bash)
source venv/bin/activate

# Or on Windows PowerShell
.\venv\Scripts\Activate.ps1

# Or on Windows CMD
venv\Scripts\activate.bat
```

You should see `(venv)` in your terminal prompt.

### Step 2: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Google Generative AI (Gemini SDK)
- GitPython, Docker SDK, and more

### Step 3: Configure Environment Variables

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file**:
   ```bash
   nano .env  # or use your preferred editor (vim, code, etc.)
   ```

3. **Configure these variables**:

   ```bash
   # Your Gemini API key from Google AI Studio
   GEMINI_API_KEY=AIza... (paste your actual key here)
   
   # Security token (already generated, or generate new one)
   AGENT_SECRET_TOKEN=e9c0ee4990529d85d09acf6cf035124dade8181ff37627b5637f96fe5c6a6bfb
   
   # Project root - where your code projects live
   # Linux/Mac example:
   PROJECT_ROOT=/home/user/projects
   
   # Windows example:
   PROJECT_ROOT=C:\\Users\\YourName\\Projects
   ```

4. **Important notes**:
   - `GEMINI_API_KEY`: Replace with your actual API key from Google
   - `AGENT_SECRET_TOKEN`: Keep this secure! It's your authentication key
   - `PROJECT_ROOT`: Must be an absolute path to an existing directory
   - On Windows, use double backslashes (`\\`) in paths

### Step 4: Test Backend

```bash
# Make sure you're in /home/user/local-ai-agent with venv activated
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process...
INFO:     Started server process...
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test it**: Open a browser to http://127.0.0.1:8000
- You should see: `{"message": "Local Agent is running. Status: OK."}`

**View API docs**: http://127.0.0.1:8000/docs
- Interactive Swagger documentation of all endpoints

Keep this terminal running!

## Frontend Configuration

Open a **new terminal window**.

### Step 1: Navigate to Frontend

```bash
cd /home/user/local-ai-agent/frontend
```

### Step 2: Verify Frontend .env

The frontend `.env` should already exist with the correct token. Verify it:

```bash
cat .env
```

Should show:
```bash
REACT_APP_AGENT_API_KEY=e9c0ee4990529d85d09acf6cf035124dade8181ff37627b5637f96fe5c6a6bfb
```

**Critical**: This must match the `AGENT_SECRET_TOKEN` in the backend `.env`!

### Step 3: Install Frontend Dependencies

```bash
npm install
```

This installs React, TypeScript, react-markdown, and all dependencies.

You may see some vulnerability warnings - this is common with npm. For a local development project, these are generally safe to ignore.

### Step 4: Start Frontend

```bash
npm start
```

You should see:
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

Your browser should automatically open to http://localhost:3000

## Testing the Installation

### Visual Test

1. You should see a header: **"Local AI Agent Control Panel"**
2. Below it, a chat interface with an input box
3. Type something simple: `Hello`
4. Press Enter or click "Send"

### Expected Behavior

- The message appears as a blue bubble on the right (user message)
- After a moment, you see "..." indicating the agent is thinking
- A response appears as a grey bubble on the left (assistant message)

### Test System Awareness

Try: `What git repositories do you see?`

The agent should:
1. Call the git status tool
2. Report on any repositories in your `PROJECT_ROOT`
3. Show information about branches, uncommitted changes, etc.

### Test Docker (if installed)

Try: `List all Docker containers`

The agent should show all your containers with their status.

## Common Issues

### Issue: "GEMINI_API_KEY not set"

**Solution**: 
- Check your backend `.env` file
- Ensure `GEMINI_API_KEY=` has your actual API key (no spaces)
- Restart the backend server

### Issue: "AGENT_SECRET_TOKEN not found"

**Solution**:
- Your backend `.env` file is missing or incomplete
- Copy `.env.example` to `.env` and configure it
- Restart the backend

### Issue: Frontend shows "Error: Could not connect to the local agent"

**Solutions**:
1. **Backend not running**: Check Terminal 1 - backend must be running on port 8000
2. **Port conflict**: Something else is using port 8000
   - Find and stop it: `lsof -i :8000` (Linux/Mac)
   - Or change the port in both `main.py` and `frontend/src/api.ts`
3. **Token mismatch**: Verify frontend and backend tokens match exactly

### Issue: "Invalid or missing authentication token"

**Solutions**:
- Frontend `.env` and backend `.env` tokens don't match
- Copy the `AGENT_SECRET_TOKEN` from backend `.env` to frontend `.env` as `REACT_APP_AGENT_API_KEY`
- Restart the frontend (Ctrl+C and `npm start` again)

### Issue: "PROJECT_ROOT environment variable not set"

**Solution**:
- Add `PROJECT_ROOT=/path/to/your/projects` to backend `.env`
- Make sure the path exists and is an absolute path
- Restart backend

### Issue: Python "ModuleNotFoundError"

**Solution**:
- Virtual environment not activated
- Run: `source venv/bin/activate` (or Windows equivalent)
- Try again: `pip install -r requirements.txt`

### Issue: npm errors during install

**Solutions**:
1. Clear npm cache: `npm cache clean --force`
2. Delete node_modules: `rm -rf node_modules package-lock.json`
3. Reinstall: `npm install`

### Issue: Docker tools return errors

**Solutions**:
1. **Docker not running**: Start Docker Desktop (or `sudo systemctl start docker` on Linux)
2. **Permission denied**: Add your user to docker group
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```
3. **Not installed**: Docker tools are optional - other features still work

## Next Steps

Once everything is working:

1. **Explore the agent's capabilities** - Try various prompts
2. **Read the main README** - Learn about adding custom tools
3. **Customize PROJECT_ROOT** - Point it to your actual projects
4. **Experiment safely** - The agent is sandboxed to PROJECT_ROOT

## Getting Help

- Check backend logs in Terminal 1 for detailed errors
- Check browser console (F12) for frontend errors
- Review the troubleshooting section in README.md
- Ensure all prerequisites are met

---

**Remember**: Always keep both terminal windows running (backend and frontend) for the system to work!
