# Quick Reference Card

## Starting the System

```bash
# Terminal 1: Backend
cd /home/user/local-ai-agent
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd /home/user/local-ai-agent/frontend
npm start
```

Or use the convenience scripts:
```bash
# Terminal 1
./start-backend.sh

# Terminal 2
./start-frontend.sh
```

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## File Locations

### Configuration
- Backend config: `/home/user/local-ai-agent/.env`
- Frontend config: `/home/user/local-ai-agent/frontend/.env`

### Code
- Backend main: `/home/user/local-ai-agent/main.py`
- Security: `/home/user/local-ai-agent/security.py`
- Tools: `/home/user/local-ai-agent/tools/*.py`
- Frontend UI: `/home/user/local-ai-agent/frontend/src/`

## Environment Variables

### Backend (.env)
```bash
GEMINI_API_KEY=your_key
AGENT_SECRET_TOKEN=64_char_hex
PROJECT_ROOT=/path/to/projects
```

### Frontend (.env)
```bash
REACT_APP_AGENT_API_KEY=same_64_char_hex
```

## Common Commands

### Backend
```bash
# Activate venv
source venv/bin/activate

# Install/update deps
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

### Frontend
```bash
# Install deps
npm install

# Start dev server
npm start

# Build for production
npm run build
```

## Example Prompts

```
"Check the status of all my repositories"
"Commit changes in /path/to/repo with message 'Fix bug'"
"List all Docker containers"
"Start the postgres-db container"
"What files are in /home/user/projects/my-app"
```

## Troubleshooting

### Backend won't start
- Check `.env` file exists and has all variables
- Verify venv is activated: `which python` should show venv path
- Check port 8000 is free: `lsof -i :8000`

### Frontend can't connect
- Verify backend is running
- Check tokens match in both .env files
- Open browser console (F12) for errors

### "Invalid token" error
- Tokens must match exactly between frontend and backend
- No spaces, quotes, or extra characters
- Must be 64 hex characters

## API Endpoints (Protected)

All require `Authorization: Bearer <token>` header:

- `GET /api/tools/git/status` - Check all repos
- `POST /api/tools/git/commit` - Commit changes
- `POST /api/tools/git/clean` - Clean repo (destructive!)
- `GET /api/tools/docker/list` - List containers
- `POST /api/tools/docker/start` - Start container
- `GET /api/tools/fs/list?path=...` - List directory
- `POST /api/chat` - Chat with AI orchestrator

## Security Features

✅ Bearer token authentication on all endpoints
✅ Strict CORS (only localhost:3000)
✅ Filesystem sandboxing (PROJECT_ROOT only)
✅ No cloud-to-local access (one-way only)
✅ Secrets in .env files (not in code)

## Architecture

```
Frontend (React)
    ↓ HTTPS + Token
Backend (FastAPI)
    ↓ Outbound only
Gemini API
```

## Adding New Tools

1. Create tool function in `tools/new_tool.py`
2. Add API endpoint in `main.py`
3. Define FunctionDeclaration for Gemini
4. Update execute_tool() mapping
5. Test with a prompt

## Getting Help

- **Setup issues**: See SETUP_GUIDE.md
- **Usage examples**: See USAGE_EXAMPLES.md
- **Full docs**: See README.md
- **Logs**: Check both terminal windows for errors

## Project Structure

```
local-ai-agent/
├── main.py              # FastAPI app
├── security.py          # Auth
├── tools/               # Automation
├── frontend/            # React UI
├── .env                 # Backend config
├── requirements.txt     # Python deps
├── README.md           # Full documentation
├── SETUP_GUIDE.md      # Detailed setup
└── USAGE_EXAMPLES.md   # Prompt examples
```

## Status Check

Backend is working if:
- http://127.0.0.1:8000 shows status message
- http://127.0.0.1:8000/docs shows API docs

Frontend is working if:
- http://localhost:3000 shows chat interface
- Can type and send messages

Full system is working if:
- Send "Hello" → get natural language response
- Send "Check git status" → gets repo information

---

**Pro Tip**: Keep this file open while developing!
