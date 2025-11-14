# Usage Examples & Prompt Guide

This guide demonstrates the capabilities of your Local AI Agent with real-world examples.

## Understanding State Awareness

Your agent is **state-aware**, meaning it automatically checks the current state of your system before taking action. This prevents redundant operations and ensures safety.

### How It Works

Every time you send a message, the agent:
1. Scans all git repositories in your `PROJECT_ROOT`
2. Checks all Docker containers
3. Sends this snapshot to Gemini along with your prompt
4. Gemini uses this context to make intelligent decisions

## Git Operations

### Check Repository Status

**Prompt**: `Check the status of all my repositories`

**What happens**:
- Agent scans `PROJECT_ROOT` for git repositories
- Reports on each repo: branch name, uncommitted changes, untracked files

**Example response**:
```
I found 3 repositories in your project directory:

1. **my-app** (main branch)
   - Has 2 uncommitted changes
   - 1 untracked file

2. **website** (develop branch)
   - Clean working directory

3. **scripts** (master branch)
   - Has 5 untracked files
```

### Commit Changes

**Prompt**: `Commit all changes in /home/user/projects/my-app with message "Fix login bug"`

**What happens**:
- Agent checks if repository is dirty
- Stages all changes (`git add .`)
- Creates commit with your message
- Reports success

**Safety**: Agent won't commit if there are no changes.

### Advanced Git Prompts

```
"Show me which repos have uncommitted work"
"Commit the changes in my-app with message 'Update documentation'"
"Are any of my repositories dirty?"
"What branch is my-app on?"
```

### Dangerous Operation: Clean Repository

**Prompt**: `Clean the my-app repository`

**What happens**:
1. Agent recognizes this is destructive
2. Asks for explicit confirmation
3. Only proceeds if you confirm

**Agent response**:
```
⚠️ WARNING: Cleaning a repository will permanently delete all untracked 
files and directories. This cannot be undone.

Are you absolutely sure you want to clean /home/user/projects/my-app?

Please confirm by responding "yes, clean it" or cancel with "no"
```

## Docker Operations

### List Containers

**Prompt**: `Show me all my Docker containers`

**What happens**:
- Agent queries Docker daemon
- Lists all containers (running and stopped)

**Example response**:
```
I found 4 Docker containers:

Running:
- postgres-db (postgres:13) - running
- redis-cache (redis:alpine) - running

Stopped:
- old-nginx (nginx:latest) - exited
- test-mongo (mongo:4.4) - exited
```

### Start a Container

**Prompt**: `Start the postgres-db container`

**What happens**:
- Agent checks current container status
- If already running, informs you (no action)
- If stopped, starts it and confirms

**Example responses**:

If already running:
```
The container 'postgres-db' is already running. No action needed.
```

If stopped:
```
I've started the 'postgres-db' container. It's now running successfully.
```

### Docker Prompt Variations

```
"List only running containers"
"Start the redis-cache container"
"Show me all containers including stopped ones"
"Is my database container running?"
```

## Filesystem Operations

### List Directory Contents

**Prompt**: `What files are in /home/user/projects/my-app`

**What happens**:
- Agent lists all files and subdirectories
- Categorizes them for clarity

**Example response**:
```
In /home/user/projects/my-app:

Directories:
- src
- tests
- docs
- node_modules

Files:
- package.json
- README.md
- .gitignore
- tsconfig.json
```

### Safety: Sandboxing

**Prompt**: `List files in /root` (outside PROJECT_ROOT)

**What happens**:
- Agent denies the request
- Explains the security boundary

**Response**:
```
Access denied. I can only access directories within my designated 
project root: /home/user/projects

This is a security feature to protect your system.
```

## Conversational Intelligence

### Natural Language Understanding

The agent understands intent, not just keywords:

❌ **Bad** (robotic): `tool_list_containers all=true`
✅ **Good** (natural): `Show me all my containers`

❌ **Bad**: `git_commit repo=/home/user/projects/app msg="fix"`
✅ **Good**: `Commit my changes in the app project with message "fix bug"`

### Context-Aware Responses

**Scenario**: You have a container already running

**Prompt**: `Start the database`

**Agent's thinking** (behind the scenes):
1. Checks Docker state snapshot
2. Sees `postgres-db` is status "running"
3. Responds intelligently

**Response**: 
```
Your database container (postgres-db) is already running, so there's 
nothing I need to do. Is there something else you'd like me to help with?
```

## Complex Workflows

### Development Setup

**Prompt**: `I'm starting work on my-app. Check if there are uncommitted changes and start the database.`

**What happens**:
1. Agent checks git status of my-app
2. Reports findings
3. Checks Docker status
4. Starts database if needed

**Example response**:
```
Here's the status of your development environment:

Git Status (my-app):
- You're on the 'develop' branch
- You have 3 uncommitted files (src/app.ts, tests/app.test.ts, README.md)
- Would you like me to commit these first?

Docker Status:
- Your postgres-db container was stopped
- I've started it for you - it's now running

You're all set to start coding!
```

### Batch Operations

**Prompt**: `Check all my repos and tell me which ones need commits`

**What happens**:
- Agent scans all repositories
- Filters to only those with changes
- Presents a summary

## Best Practices

### 1. Be Conversational

✅ **Good**:
```
"Hey, are any of my projects uncommitted?"
"Can you check what Docker containers are running?"
"Start my database please"
```

❌ **Avoid**:
```
"execute git status all repos"
"run docker ps command"
```

### 2. Let the Agent Decide HOW

You specify **what**, agent figures out **how**:

✅ `"I need to save my work on the my-app project"`
- Agent determines: needs git add + commit
- Asks for commit message
- Executes steps

### 3. Confirm Destructive Actions

For operations that delete data:
- Agent will always ask for confirmation
- Be explicit: "yes, clean it" not just "ok"

### 4. Use State Awareness

Instead of:
```
"List containers"
[sees output]
"Start postgres-db"
```

Try:
```
"Make sure my database is running"
```
Agent will check state and only start if needed.

## Error Handling

### Agent Can't Complete Task

**Example prompt**: `Start the nonexistent-container`

**Response**:
```
I tried to start the container 'nonexistent-container', but I got an error:

Error: Container 'nonexistent-container' not found.

Would you like me to list your available containers?
```

### Permission Issues

**Example**: Docker daemon not running

**Response**:
```
I couldn't connect to the Docker daemon. It appears Docker isn't running 
or I don't have permission to access it.

Please check:
1. Is Docker Desktop running?
2. Do you have permission to use Docker?
```

## Advanced Tips

### 1. Chaining Requests

```
"Check my repos, commit any changes, then start my database"
```

Agent will execute in sequence and report on each step.

### 2. Asking for Advice

```
"I have uncommitted changes in 3 repos. What should I commit first?"
```

Agent will analyze and make recommendations based on context.

### 3. Status Checks

```
"Give me a full status of my development environment"
```

Gets comprehensive overview of git and docker state.

## What the Agent CAN'T Do (Yet)

Current limitations:
- Can't execute arbitrary shell commands
- Can't modify files directly
- Can't push to remote git repositories
- Can't stop/restart Docker containers (only start)
- Can't create new directories or files

These limitations are **by design** for security. Future versions may add more capabilities with proper safeguards.

## Extending Capabilities

Want to add new tools? See README.md "Adding New Tools" section.

Ideas for custom tools:
- AWS/Azure operations
- Database queries
- Log file analysis
- Build system automation
- Custom deployment scripts

---

**Remember**: The agent is most powerful when you communicate naturally and let it leverage its state awareness!
