# Video Foundry - Windows Setup Guide

Complete guide for setting up and using Video Foundry on Windows (without WSL).

---

## 📋 Prerequisites

### Required Software

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Ensure Docker Desktop is running before starting

2. **Git for Windows**
   - Download: https://git-scm.com/download/win
   - Includes Git Bash (optional but useful)

3. **PowerShell 5.1+** (included with Windows 10/11)
   - Check version: `$PSVersionTable.PSVersion`

### Optional (for local development)

4. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

5. **Node.js 18+**
   - Download: https://nodejs.org/
   - Includes npm

---

## 🚀 Quick Start

### 1. Clone the Repository

```powershell
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco
```

### 2. Set Execution Mode

For development:
```powershell
# Copy developer environment template
Copy-Item .env.developer.example .env

# Edit .env if needed (optional for basic setup)
notepad .env
```

### 3. Start Services

Using PowerShell automation:
```powershell
.\dev.ps1 up
```

Or using Docker Compose directly:
```powershell
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ComfyUI**: http://localhost:8188
- **RabbitMQ**: http://localhost:15672 (guest/guest)

---

## 💻 Windows Automation Tools

### PowerShell Development Script (`dev.ps1`)

The main automation tool for Windows - equivalent to the Makefile on Linux/Mac.

**Usage:**
```powershell
.\dev.ps1 <command>
```

**Common Commands:**

```powershell
# Service Management
.\dev.ps1 up              # Start all services
.\dev.ps1 down            # Stop all services
.\dev.ps1 restart         # Restart services
.\dev.ps1 status          # Show service status

# Development
.\dev.ps1 dev             # Start with logs visible
.\dev.ps1 logs            # View logs
.\dev.ps1 logs-backend    # View backend logs only

# Testing
.\dev.ps1 test            # Run all tests
.\dev.ps1 test-unit       # Run unit tests (fast)

# Code Quality
.\dev.ps1 lint            # Check code quality
.\dev.ps1 format          # Format code

# Database
.\dev.ps1 db-shell        # Open PostgreSQL shell
.\dev.ps1 redis-cli       # Open Redis CLI

# Utilities
.\dev.ps1 shell-backend   # Shell in backend container
.\dev.ps1 health          # Check service health
.\dev.ps1 clean           # Clean up containers

# Help
.\dev.ps1 help            # Show all commands
```

### PowerShell Scripts (in `scripts/`)

Individual scripts for specific tasks:

```powershell
# Environment check
.\scripts\dev-check.ps1

# Quick testing
.\scripts\quick-test.ps1          # Unit tests
.\scripts\quick-test.ps1 all      # All tests

# Code quality
.\scripts\code-check.ps1          # Check code

# Auto-fix issues
.\scripts\auto-fix.ps1            # Fix formatting & linting
```

---

## 🛠️ Development Workflow (Windows)

### Starting Your Day

```powershell
# 1. Check your environment
.\scripts\dev-check.ps1

# 2. Start services
.\dev.ps1 dev

# 3. (In another PowerShell window) Run tests
.\scripts\quick-test.ps1
```

### Making Changes

```powershell
# 1. Make your changes in your editor

# 2. Check code quality
.\scripts\code-check.ps1

# 3. Auto-fix issues
.\scripts\auto-fix.ps1

# 4. Test your changes
.\scripts\quick-test.ps1

# 5. Commit
git add .
git commit -m "Your message"
```

### Debugging

```powershell
# View logs
.\dev.ps1 logs-backend

# Check service health
.\dev.ps1 health

# Get shell in container
.\dev.ps1 shell-backend

# Check database
.\dev.ps1 db-shell
# Then run SQL: SELECT * FROM projects;

# Check Redis
.\dev.ps1 redis-cli
# Then run: KEYS *
```

---

## 📦 Installing Dependencies

### Python Dependencies

```powershell
# All dependencies
.\dev.ps1 install

# Backend only
pip install -r backend\requirements.txt

# Development tools
pip install -r requirements-dev.txt
```

### Frontend Dependencies

```powershell
# Using dev.ps1
.\dev.ps1 install-frontend

# Or directly
cd frontend
npm install
cd ..
```

---

## 🔧 Configuration

### Environment Variables

Windows uses `.env` files just like Linux. Choose the appropriate template:

**For Development:**
```powershell
Copy-Item .env.developer.example .env
```

**For Self-Hosted Production:**
```powershell
Copy-Item .env.self-hosted.example .env
# Edit with your values
notepad .env
```

**For Production (Multi-tenant SaaS):**
```powershell
Copy-Item .env.production.example .env
# Edit with your values
notepad .env
```

### Execution Mode

Set in `.env` file:
```bash
# Developer mode (default for local work)
JYNCO_EXECUTION_MODE=developer

# Self-hosted production
JYNCO_EXECUTION_MODE=self-hosted-production

# Production (multi-tenant SaaS)
JYNCO_EXECUTION_MODE=production
```

---

## 🧪 Testing

### Run Tests

```powershell
# All tests
.\dev.ps1 test

# Unit tests only (fast)
.\dev.ps1 test-unit
.\scripts\quick-test.ps1

# Integration tests
.\dev.ps1 test-integration

# With coverage
.\dev.ps1 test-cov
```

### Frontend Tests

```powershell
.\dev.ps1 test-frontend
```

---

## 🔍 Code Quality

### Linting

```powershell
# Check Python code
.\dev.ps1 lint-backend

# Check frontend code
.\dev.ps1 lint-frontend

# Check everything
.\dev.ps1 lint
```

### Formatting

```powershell
# Format Python code
.\dev.ps1 format-backend

# Format frontend code
.\dev.ps1 format-frontend

# Format everything
.\dev.ps1 format
```

### Auto-fix Everything

```powershell
# One command to fix all issues
.\scripts\auto-fix.ps1
```

---

## 🗄️ Database Management

### Migrations

```powershell
# Run migrations
.\dev.ps1 db-migrate

# Rollback last migration
.\dev.ps1 db-rollback

# Reset database (DANGEROUS!)
.\dev.ps1 db-reset
```

### Database Shell

```powershell
# Open psql
.\dev.ps1 db-shell

# Then run SQL commands
SELECT * FROM projects LIMIT 5;
```

---

## 🐋 Docker Management

### Service Control

```powershell
# Start all services
.\dev.ps1 up

# Start specific services
docker-compose up -d postgres redis backend

# Stop services
.\dev.ps1 down

# Restart services
.\dev.ps1 restart

# Rebuild services
.\dev.ps1 rebuild
```

### Viewing Logs

```powershell
# All logs
.\dev.ps1 logs

# Specific service
.\dev.ps1 logs-backend
.\dev.ps1 logs-frontend
.\dev.ps1 logs-workers
.\dev.ps1 logs-comfyui

# Follow logs (real-time)
docker-compose logs -f backend
```

### Scaling Workers

```powershell
# Scale AI workers to 4 instances
.\dev.ps1 scale-workers 4
```

---

## 🧹 Cleanup

### Clean Docker Resources

```powershell
# Remove containers and volumes
.\dev.ps1 clean

# Remove images too
.\dev.ps1 clean-images

# Nuclear option - remove everything
.\dev.ps1 clean-all
```

### Clean Python Cache

```powershell
# Remove __pycache__ and .pyc files
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | Remove-Item -Force
```

---

## 🚨 Troubleshooting

### Docker Desktop Not Running

**Error:** `error during connect: ... Is the docker daemon running?`

**Solution:**
1. Start Docker Desktop
2. Wait for it to fully start (whale icon in system tray)
3. Try command again

### Port Already in Use

**Error:** `Bind for 0.0.0.0:5173 failed: port is already allocated`

**Solution:**
```powershell
# Find process using port 5173
Get-NetTCPConnection -LocalPort 5173 | Select-Object OwningProcess
Stop-Process -Id <ProcessID>

# Or restart Docker Desktop
```

### PowerShell Execution Policy

**Error:** `.\dev.ps1 : File cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
# Allow scripts for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run specific script
PowerShell -ExecutionPolicy Bypass -File .\dev.ps1 up
```

### Services Won't Start

```powershell
# Check Docker Desktop is running
docker info

# Check service status
.\dev.ps1 status

# View logs
.\dev.ps1 logs

# Reset everything
.\dev.ps1 clean
.\dev.ps1 up
```

### Tests Failing

```powershell
# Ensure services are running
.\dev.ps1 status

# Check service health
.\dev.ps1 health

# View test output
.\dev.ps1 test-unit

# Reset database
.\dev.ps1 db-reset
```

---

## 📚 Additional Resources

### Documentation

- [Main README](README.md) - Project overview
- [Automation Guide](AUTOMATION_GUIDE.md) - Full automation reference
- [Security Proposal](docs/SECURITY_PROPOSAL_V3.md) - Security architecture
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines

### External Links

- [Docker Desktop Documentation](https://docs.docker.com/desktop/windows/)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Git for Windows](https://gitforwindows.org/)

---

## 💡 Tips & Best Practices

### PowerShell Tips

1. **Tab Completion:** Type `.\dev.ps1 ` and press Tab to see commands
2. **Command History:** Use Up/Down arrows for previous commands
3. **Copy/Paste:** Right-click to paste in PowerShell

### Development Tips

1. **Use Multiple Terminals:**
   - Terminal 1: `.\dev.ps1 dev` (watch logs)
   - Terminal 2: Run tests and commands

2. **Quick Environment Check:**
   ```powershell
   .\scripts\dev-check.ps1
   ```

3. **Before Committing:**
   ```powershell
   .\scripts\auto-fix.ps1
   .\scripts\quick-test.ps1
   git add .
   git commit -m "Your message"
   ```

### Performance Tips

1. **Enable WSL 2 Backend in Docker Desktop** (if available)
   - Settings → General → "Use WSL 2 based engine"
   - Significantly faster than Hyper-V

2. **Allocate More Resources to Docker**
   - Settings → Resources
   - Increase CPUs and Memory for better performance

3. **Use `.dockerignore`**
   - Already configured in the project
   - Speeds up build times

---

## 🔐 Security Notes

### Developer Mode

When using developer mode on Windows:
- ✅ Safe for local development
- ⚠️ Use Windows Firewall to block external access
- ⚠️ Never use production credentials
- ⚠️ Only run on trusted networks

### Firewall Configuration

```powershell
# Check if port is blocked (as administrator)
Get-NetFirewallRule | Where-Object {$_.LocalPort -eq 5173}

# Block port from external access (as administrator)
New-NetFirewallRule -DisplayName "Block Video Foundry External" `
    -Direction Inbound -LocalPort 5173 -Protocol TCP `
    -RemoteAddress !127.0.0.1 -Action Block
```

---

## 📞 Getting Help

### Quick Help

```powershell
# Show all dev.ps1 commands
.\dev.ps1 help

# Check environment
.\scripts\dev-check.ps1

# Check service health
.\dev.ps1 health
```

### Support Channels

- **Documentation**: This guide and [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/QFiSouthaven/Jynco/issues)
- **Discussions**: [GitHub Discussions](https://github.com/QFiSouthaven/Jynco/discussions)

---

## 🎉 You're All Set!

Your Windows development environment is ready. Start developing with:

```powershell
.\dev.ps1 up
# Visit http://localhost:5173
```

Happy coding! 🚀
