# Video Foundry - Automation & Development Guide

This guide covers all automation tools and workflows for seamless development with Claude Code.

## 🚀 Quick Start

```bash
# First time setup
make setup              # Install everything and start services
./scripts/dev-check.sh  # Verify your environment

# Daily workflow
make dev                # Start services with logs
make test               # Run tests
make logs               # Check logs
```

---

## 📚 Table of Contents

1. [Makefile Commands](#makefile-commands)
2. [Automation Scripts](#automation-scripts)
3. [Pre-commit Hooks](#pre-commit-hooks)
4. [Claude Code Integration](#claude-code-integration)
5. [Development Workflows](#development-workflows)
6. [Best Practices](#best-practices)

---

## Makefile Commands

The Makefile provides **60+ commands** for common tasks. Run `make help` to see all.

### Essential Commands

```bash
# Service Management
make up                 # Start all services (detached)
make down               # Stop all services
make restart            # Restart all services
make status             # Show service status
make logs               # View all logs (live)

# Development
make dev                # Start with logs visible
make dev-backend        # Backend + dependencies only
make dev-frontend       # Frontend + backend only
make dev-workers        # Workers + dependencies only

# Testing
make test               # Run all tests
make test-unit          # Unit tests only (fast)
make test-integration   # Integration tests
make test-e2e           # End-to-end tests
make test-cov           # Tests with coverage report

# Code Quality
make lint               # Lint all code
make format             # Format all code
make check              # Lint + test everything

# Database
make db-migrate         # Run migrations
make db-rollback        # Rollback last migration
make db-reset           # Reset database (DANGEROUS!)
make db-shell           # Open psql shell
make redis-cli          # Open Redis CLI

# Monitoring
make health             # Check all service health
make logs-backend       # Backend logs only
make logs-workers       # Worker logs only
make logs-frontend      # Frontend logs only
make logs-comfyui       # ComfyUI logs only

# Utilities
make shell-backend      # Shell in backend container
make shell-worker       # Shell in worker container
make scale-workers N=4  # Scale AI workers to 4 instances

# Cleanup
make clean              # Remove containers and volumes
make clean-images       # Remove images too
make clean-all          # Nuclear option - remove everything
```

### Advanced Usage

```bash
# Chain commands
make lint && make test && make up

# Quick testing workflow
make quick-test         # Starts services + runs tests

# Scale workers for heavy workload
make scale-workers N=10

# Watch status continuously
make watch
```

---

## Automation Scripts

Located in `scripts/` directory - run anytime for quick checks.

### 1. Environment Check

```bash
./scripts/dev-check.sh
```

**What it does:**
- Verifies Docker is running
- Checks required tools (git, make, curl)
- Validates Python and Node.js versions
- Checks .env configuration
- Reports disk space

**When to use:** Before starting work, after system updates, troubleshooting

### 2. Quick Test Runner

```bash
./scripts/quick-test.sh [unit|integration|all|watch]
```

**Examples:**
```bash
./scripts/quick-test.sh              # Unit tests (fast, default)
./scripts/quick-test.sh integration  # Integration tests
./scripts/quick-test.sh all          # Everything
./scripts/quick-test.sh watch        # Watch mode (re-run on changes)
```

**When to use:** During development, before commits

### 3. Code Quality Check

```bash
./scripts/code-check.sh
```

**What it does:**
- Checks for large files (>10MB)
- Runs Ruff linter on Python code
- Checks code formatting
- Scans for secrets
- Checks dependencies for vulnerabilities

**When to use:** Before commits, before PRs

### 4. Auto-fix Issues

```bash
./scripts/auto-fix.sh
```

**What it does:**
- Auto-fixes Python linting issues
- Formats all Python code
- Fixes frontend code (if scripts exist)
- Removes trailing whitespace
- Fixes line endings

**When to use:** After writing code, before committing

---

## Pre-commit Hooks

Automatically run checks before every commit to catch issues early.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks in your repo
pre-commit install

# Test it works
pre-commit run --all-files
```

### What Gets Checked

Every commit automatically runs:

1. **General Checks**
   - Trailing whitespace removed
   - End-of-file fixed
   - YAML/JSON validated
   - Large files detected
   - Merge conflicts detected
   - Private keys detected

2. **Python (Backend/Workers)**
   - Ruff linting + auto-fix
   - Ruff formatting
   - MyPy type checking
   - Bandit security checks

3. **Frontend**
   - ESLint with auto-fix
   - Prettier formatting

4. **Docker**
   - Dockerfile linting

5. **Documentation**
   - Markdown linting

### Skip Hooks (When Needed)

```bash
# Skip all hooks
git commit --no-verify -m "Emergency fix"

# Skip specific hook
SKIP=ruff git commit -m "WIP: Working on it"

# Skip multiple hooks
SKIP=ruff,mypy git commit -m "Quick fix"
```

---

## Claude Code Integration

### Session Start Hook

Automatically runs when you start a Claude Code session.

**Location:** `.claude/hooks/session-start.sh`

**What it shows:**
- Service status (✅ running or ❌ down)
- Quick links to all dashboards
- Common commands
- Git status summary

**Customize it:**
Edit `.claude/hooks/session-start.sh` to add project-specific checks.

### Custom Commands (Future)

You can add custom slash commands:

```bash
mkdir -p .claude/commands
echo "Run the test suite and show results" > .claude/commands/test.md
```

Then use `/test` in Claude Code to trigger it.

---

## Development Workflows

### Workflow 1: Starting Your Day

```bash
# Check everything is ready
./scripts/dev-check.sh

# Start services
make dev

# In another terminal, run tests
make test-unit

# Make changes, then auto-fix
./scripts/auto-fix.sh

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: Add new feature"
```

### Workflow 2: Feature Development

```bash
# Start services
make up

# Work on backend
make shell-backend
# (make changes in your editor)

# Watch logs for issues
make logs-backend

# Test your changes
make test-unit

# Check code quality
./scripts/code-check.sh

# Auto-fix any issues
./scripts/auto-fix.sh

# Commit
git add .
git commit -m "feat: New feature"
```

### Workflow 3: Debugging

```bash
# Check service status
make status
make health

# View specific logs
make logs-backend    # or logs-workers, logs-comfyui

# Get shell in container
make shell-backend

# Check database
make db-shell
SELECT * FROM projects LIMIT 5;

# Check Redis
make redis-cli
KEYS *

# Restart specific service
docker-compose restart backend
```

### Workflow 4: Testing Changes

```bash
# Quick unit tests while coding
./scripts/quick-test.sh

# Watch mode (auto-run on file changes)
./scripts/quick-test.sh watch

# Full test suite before committing
make test

# Test with coverage
make test-cov
# Open htmlcov/index.html to see report

# Integration tests (services must be running)
make up
make test-integration
```

### Workflow 5: Scaling Workers

```bash
# For heavy video generation workload
make up
make scale-workers N=5

# Monitor worker logs
make logs-workers

# Scale back down
make scale-workers N=1
```

---

## Best Practices

### Code Quality

1. **Always run auto-fix before committing**
   ```bash
   ./scripts/auto-fix.sh
   git add .
   git commit -m "Your message"
   ```

2. **Run tests frequently**
   ```bash
   # While coding (fast)
   ./scripts/quick-test.sh

   # Before committing
   make test
   ```

3. **Use pre-commit hooks**
   - Never skip them unless absolutely necessary
   - If you skip, fix issues immediately after

### Docker Management

1. **Keep containers running**
   ```bash
   make up   # Start once, leave running
   ```

2. **Only rebuild when needed**
   ```bash
   make rebuild   # After dependency changes
   ```

3. **Clean up regularly**
   ```bash
   make clean     # Remove unused volumes
   ```

### Testing Strategy

1. **Unit tests first** (fast feedback)
2. **Integration tests** (before PRs)
3. **E2E tests** (before releases)

```bash
# Development cycle
./scripts/quick-test.sh              # Unit tests (fast)

# Pre-commit
make test-unit                       # Verify units pass

# Pre-PR
make test                            # Full test suite

# Pre-release
make test-e2e                        # End-to-end
```

### Performance Tips

1. **Use make targets** (faster than docker-compose)
   ```bash
   make up      # Instead of: docker-compose up -d
   ```

2. **Parallel testing**
   ```bash
   pytest -n auto    # Use all CPU cores
   ```

3. **Watch mode for development**
   ```bash
   ./scripts/quick-test.sh watch
   ```

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker
./scripts/dev-check.sh

# Check ports
make status

# View logs
make logs

# Reset everything
make clean
make up
```

### Tests Failing

```bash
# Check services are running
make health

# View test output
make test-unit

# Check specific test
pytest tests/test_specific.py -v

# Reset database
make db-reset
```

### Code Quality Issues

```bash
# Auto-fix everything
./scripts/auto-fix.sh

# Check what's wrong
./scripts/code-check.sh

# Manual fixes
ruff check --fix backend/
ruff format backend/
```

### Pre-commit Hooks Failing

```bash
# See what failed
pre-commit run --all-files

# Auto-fix issues
./scripts/auto-fix.sh

# Try commit again
git commit -m "Your message"

# Emergency skip (use sparingly!)
git commit --no-verify -m "Emergency fix"
```

---

## Integration with Claude Code

### Typical Session Flow

1. **Claude sees session start hook output**
   - Service status
   - Git status
   - Quick actions

2. **You request a feature or fix**

3. **Claude can use automation:**
   ```bash
   # Check environment
   ./scripts/dev-check.sh

   # Make changes
   # ...

   # Auto-fix code
   ./scripts/auto-fix.sh

   # Run tests
   make test-unit

   # Commit
   git add .
   git commit -m "feat: New feature"
   ```

### Commands Claude Should Use

**For checking:**
- `make status` - Service status
- `make health` - Health checks
- `./scripts/dev-check.sh` - Full environment check

**For testing:**
- `./scripts/quick-test.sh` - Fast tests
- `make test-unit` - Unit tests
- `make test` - Full suite

**For code quality:**
- `./scripts/code-check.sh` - Check issues
- `./scripts/auto-fix.sh` - Fix automatically
- `make lint` - Run linters

**For viewing:**
- `make logs-[service]` - View logs
- `make status` - Container status

---

## Quick Reference Card

Print this out or keep it handy:

```
╔═══════════════════════════════════════════════════════════╗
║         VIDEO FOUNDRY - AUTOMATION QUICK REFERENCE         ║
╠═══════════════════════════════════════════════════════════╣
║ DAILY COMMANDS                                             ║
║   make dev              Start services with logs           ║
║   make test             Run tests                          ║
║   make logs             View logs                          ║
║   make status           Check status                       ║
║                                                             ║
║ CODE QUALITY                                               ║
║   ./scripts/auto-fix.sh Auto-fix issues                    ║
║   ./scripts/code-check.sh  Check quality                   ║
║   make lint             Lint code                          ║
║   make format           Format code                        ║
║                                                             ║
║ TESTING                                                    ║
║   ./scripts/quick-test.sh  Fast unit tests                 ║
║   make test-unit        Unit tests                         ║
║   make test-integration Integration tests                  ║
║   make test-cov         Coverage report                    ║
║                                                             ║
║ DEBUGGING                                                  ║
║   make health           Health checks                      ║
║   make logs-backend     Backend logs                       ║
║   make shell-backend    Shell in backend                   ║
║   make db-shell         Database shell                     ║
║                                                             ║
║ SETUP                                                      ║
║   make setup            Initial setup                      ║
║   ./scripts/dev-check.sh  Verify environment               ║
║   pre-commit install    Install hooks                      ║
║                                                             ║
║ HELP                                                       ║
║   make help             Show all commands                  ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Next Steps

1. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Install Ruff for fast linting:**
   ```bash
   pip install ruff
   ```

3. **Try the automation:**
   ```bash
   ./scripts/dev-check.sh
   make dev
   ./scripts/quick-test.sh
   ```

4. **Customize for your needs:**
   - Edit `.claude/hooks/session-start.sh`
   - Add custom make targets to `Makefile`
   - Create project-specific scripts in `scripts/`

---

## Support

For issues with automation tools:
1. Check this guide
2. Run `make help`
3. Open an issue on GitHub

Happy coding! 🚀
