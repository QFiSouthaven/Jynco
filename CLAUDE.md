# CLAUDE.md - Video Foundry (Jynco) Codebase Guide

**Last Updated:** November 14, 2025  
**Project Version:** 1.0.0 (Production Ready)  
**Repository:** github.com/QFiSouthaven/Jynco  
**License:** MIT

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Directory Structure](#directory-structure)
5. [Backend Structure](#backend-structure)
6. [Frontend Structure](#frontend-structure)
7. [Development Workflows](#development-workflows)
8. [Building and Testing](#building-and-testing)
9. [Configuration Management](#configuration-management)
10. [Code Organization Patterns](#code-organization-patterns)
11. [Key Concepts](#key-concepts)
12. [Common Development Tasks](#common-development-tasks)
13. [Deployment](#deployment)

---

## Project Overview

**Video Foundry** is a scalable, production-ready AI video generation platform combining timeline-based editing with seamless ComfyUI integration. It enables users to generate, compose, and manage AI-powered video content at scale.

### Key Characteristics
- **Timeline-Based Editing**: Visual drag-and-drop interface for managing multi-segment video projects
- **AI Model Flexibility**: Support for Runway Gen-3, Stability AI, local ComfyUI, and custom adapters
- **Intelligent Re-rendering**: Only regenerates modified segments, saving time and resources
- **Real-time Tracking**: WebSocket-based progress monitoring for all render jobs
- **Horizontal Scaling**: Worker services scale to handle high-volume production workloads
- **Hybrid Deployment**: Works locally with ComfyUI or integrates with cloud-based AI APIs

### Core Features
1. Text-to-video generation using AnimateDiff + SDXL
2. Image-to-video animation via Stable Video Diffusion
3. Custom ComfyUI workflow creation and management
4. Batch segment processing with parallel execution
5. S3/Local storage with CDN readiness
6. Multi-user project management (user foundation in place)
7. Workflow library for template reuse

---

## Architecture

### System Overview
```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React 18)                    │
│            Timeline Editor + Project Manager             │
│              (TypeScript + TailwindCSS)                  │
└──────────────────┬──────────────────────────────────────┘
                   │
         WebSocket │ REST API
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  Projects │ Segments │ Render │ Workflows │ Health      │
└──────────┬──────────────────────────────────────────────┘
           │
    ┌──────┼──────────────────────────┐
    ▼      ▼                          ▼
┌────────┐ ┌──────────┐        ┌──────────────┐
│ Postgres│ │  Redis   │        │  RabbitMQ    │
└────────┘ └──────────┘        └──┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐  ┌──────────┐  ┌─────────────┐
              │AI Worker │  │AI Worker │  │Composition  │
              │(ComfyUI) │  │(Runway)  │  │Worker       │
              └──────────┘  └──────────┘  └──────┬──────┘
                    │             │              │
                    └─────────────┴──────────────┘
                           │
                    ┌──────▼──────┐
                    │S3 / Local   │
                    │Storage      │
                    └─────────────┘
```

### Data Flow
```
User Request (Timeline Editor)
    ↓
Backend API (validates & stores)
    ↓
RabbitMQ Queue (distributed task)
    ↓
AI Workers (parallel processing)
    ├─ Generate video segments
    └─ Store in S3/Local
    ↓
Redis (progress updates)
    ↓
WebSocket (real-time UI update)
    ↓
Composition Queue
    ↓
Composition Worker (FFmpeg)
    ↓
Final Video (S3/Local + Database)
```

### Component Responsibilities

**Frontend**: User interaction, timeline visualization, real-time progress
**Backend**: Business logic, job orchestration, database management, API gateway
**AI Workers**: Video generation via pluggable model adapters
**Composition Worker**: Video assembly, effects, transitions, final output
**Infrastructure**: Persistence, caching, messaging, async task execution

---

## Technology Stack

### Backend & Workers
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11+ | Core backend language |
| Web Framework | FastAPI | 0.109.0 | REST API & async support |
| ASGI Server | Uvicorn | 0.27.0 | Application server |
| ORM | SQLAlchemy | 2.0.25 | Database abstraction |
| Migrations | Alembic | 1.13.1 | Schema versioning |
| Validation | Pydantic | 2.5.3 | Request/response validation |
| Message Queue | RabbitMQ/Pika | 3/1.3.2 | Task distribution |
| Cache | Redis | 7 | Session & caching |
| HTTP Client | HTTPX | 0.26.0 | Async external API calls |
| Retry Logic | Tenacity | 8.2.3 | Resilience patterns |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| UI Framework | React | 18.2.0 | Component-based UI |
| Language | TypeScript | 5.3.3 | Type-safe JavaScript |
| Build Tool | Vite | 5.1.0 | Fast module bundling |
| CSS Framework | TailwindCSS | 3.4.1 | Utility-first styling |
| State Management | Zustand | 4.5.0 | Lightweight store |
| Data Fetching | Axios | 1.6.7 | HTTP client |
| Query Library | React Query | 5.17.19 | Server state management |
| Routing | React Router | 6.22.0 | Client-side routing |
| Icons | React Icons | 5.0.1 | Icon components |

### Infrastructure
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Database | PostgreSQL | 15 | Relational data persistence |
| Cache | Redis | 7 | In-memory data store |
| Message Broker | RabbitMQ | 3 | Distributed task queue |
| Container Runtime | Docker | Latest | Containerization |
| Orchestration | Docker Compose | - | Multi-container management |
| Reverse Proxy | NGINX | - | Production load balancing |
| Admin UI | Portainer | Latest | Docker management interface |

### AI Services
| Service | Purpose | Type |
|---------|---------|------|
| ComfyUI | Local video generation (AnimateDiff, SVD) | On-premise |
| Runway Gen-3 | Cloud text-to-video | API |
| Stability AI | Image/video generation | API |
| Custom Adapters | Extensible model interface | Plugin |

### Development Tools
| Tool | Purpose | Version |
|------|---------|---------|
| Ruff | Python linting & formatting | 0.1.9+ |
| MyPy | Static type checking | 1.8.0+ |
| Bandit | Security scanning | 1.7.6+ |
| Pytest | Test framework | 7.4.3+ |
| Pre-commit | Git hooks framework | 3.6.0+ |
| ESLint | Frontend linting | 8.56.0+ |
| Prettier | Code formatting | 3.1.0+ |

---

## Directory Structure

```
Jynco/
├── backend/                          # FastAPI application
│   ├── main.py                       # Application entry point
│   ├── config/
│   │   ├── settings.py              # Environment configuration
│   │   └── database.py              # Database initialization
│   ├── api/                         # API route handlers
│   │   ├── projects.py              # Project CRUD endpoints
│   │   ├── segments.py              # Segment management
│   │   ├── render.py                # Render job orchestration
│   │   ├── workflows.py             # Workflow library API
│   │   └── health.py                # Health check endpoint
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── base.py                  # Base model with timestamps
│   │   ├── project.py               # Project entity
│   │   ├── segment.py               # Video segment entity
│   │   ├── render_job.py            # Render job tracking
│   │   ├── workflow.py              # Workflow templates
│   │   └── user.py                  # User authentication
│   ├── schemas/                     # Pydantic validation schemas
│   │   ├── project.py               # ProjectCreate, ProjectUpdate, etc.
│   │   ├── segment.py               # Segment request/response
│   │   ├── render_job.py            # Job status schemas
│   │   └── workflow.py              # Workflow schemas
│   ├── services/                    # Business logic
│   │   ├── orchestrator.py          # Render job orchestration
│   │   ├── redis_client.py          # Cache service
│   │   ├── s3_client.py             # Storage abstraction
│   │   └── rabbitmq_client.py       # Message queue interface
│   ├── core/
│   │   └── security/                # Auth & security
│   ├── migrations/                  # Alembic database migrations
│   ├── requirements.txt             # Production dependencies
│   └── Dockerfile                   # Container configuration
│
├── frontend/                         # React web application
│   ├── src/
│   │   ├── main.tsx                 # Application entry
│   │   ├── App.tsx                  # Root component
│   │   ├── api/
│   │   │   ├── client.ts            # HTTP client configuration
│   │   │   ├── projects.ts          # Project API calls
│   │   │   └── workflows.ts         # Workflow API calls
│   │   ├── components/              # Reusable UI components
│   │   │   ├── Header.tsx           # Navigation header
│   │   │   ├── VideoPlayer.tsx      # Video playback
│   │   │   ├── VideoModal.tsx       # Video display modal
│   │   │   └── ComfyUIStatus.tsx    # ComfyUI health indicator
│   │   ├── features/                # Feature-specific pages
│   │   │   ├── dashboard/           # Main dashboard
│   │   │   ├── projects/            # Project list & management
│   │   │   ├── timeline/            # Timeline editor
│   │   │   │   ├── TimelineEditor.tsx
│   │   │   │   └── SegmentCard.tsx
│   │   │   └── workflows/           # Workflow library
│   │   │       └── WorkflowLibrary.tsx
│   │   ├── store/                   # Zustand state stores
│   │   │   └── useProjectStore.ts   # Project state management
│   │   ├── utils/                   # Utility functions
│   │   │   └── errorMessages.ts     # Error handling
│   │   └── index.css                # Global styles
│   ├── public/                      # Static assets
│   ├── vite.config.ts              # Vite configuration
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tailwind.config.js          # Tailwind CSS config
│   ├── package.json                # Node dependencies
│   ├── Dockerfile.dev              # Development container
│   └── index.html                  # HTML entry point
│
├── workers/                         # Distributed worker services
│   ├── ai_worker/                  # Video generation worker
│   │   ├── worker.py               # Worker entry point & loop
│   │   ├── adapters/               # AI model integrations
│   │   │   ├── base.py             # Abstract base adapter
│   │   │   ├── factory.py          # Adapter factory pattern
│   │   │   ├── comfyui.py          # ComfyUI adapter
│   │   │   ├── runway.py           # Runway Gen-3 adapter
│   │   │   ├── stability.py        # Stability AI adapter
│   │   │   ├── mock.py             # Mock adapter for testing
│   │   │   └── exceptions.py       # Custom exceptions
│   │   ├── requirements.txt        # Worker dependencies
│   │   └── Dockerfile             # Worker container
│   │
│   └── composition_worker/         # Video composition service
│       ├── worker.py               # Composition worker
│       ├── requirements.txt        # Dependencies
│       └── Dockerfile             # Container
│
├── chromaframe/                    # C++ 2D animation tool (planned)
│   ├── src/
│   │   └── main.cpp               # Application entry
│   ├── include/                    # Public headers
│   ├── CMakeLists.txt             # Build configuration
│   ├── README.md                   # Tool documentation
│   └── .gitignore
│
├── docs/                           # Comprehensive documentation
│   ├── SETUP.md                    # Installation & setup
│   ├── USER_GUIDE.md              # End-user documentation
│   ├── COMFYUI_INTEGRATION.md     # ComfyUI setup guide
│   ├── TROUBLESHOOTING.md         # Common issues & solutions
│   ├── CHROMAFRAME_ARCHITECTURE.md # Animation tool specs
│   ├── CHROMAFRAME_INTEGRATION_STRATEGY.md
│   ├── SECURITY_BEST_PRACTICES.md # Security guide
│   ├── SECURITY_PROPOSAL_V3.md    # Security architecture
│   ├── SECURITY_IMPLEMENTATION_ROADMAP.md
│   └── security/                   # Additional security docs
│
├── tests/                          # Test suite
│   ├── conftest.py                # Pytest configuration
│   ├── e2e/
│   │   └── test_timeline_workflow.py # End-to-end tests
│   └── requirements.txt            # Test dependencies
│
├── scripts/                        # Automation scripts
│   ├── dev-check.sh               # Development environment check
│   ├── code-check.sh              # Code quality checks
│   ├── quick-test.sh              # Fast test execution
│   ├── auto-fix.sh                # Automatic code formatting
│   ├── dev-check.ps1              # Windows version
│   ├── code-check.ps1
│   ├── quick-test.ps1
│   └── auto-fix.ps1
│
├── workflows/                      # ComfyUI workflow templates
│   ├── text-to-video-basic.json
│   ├── image-to-video-basic.json
│   └── README.md
│
├── sub-agents/                     # AI agent definitions
│   ├── asset-foundry-agents/      # Specialized asset creation agents
│   │   ├── Artist.md
│   │   ├── Architect.md
│   │   ├── Artificer.md
│   │   ├── Librarian.md
│   │   ├── Quartermaster.md
│   │   └── README.md
│   └── saas-framework/            # SaaS architecture frameworks
│       ├── DesirePathFramework.md
│       ├── MycelialNetworkFramework.md
│       ├── NicheEcosystemFramework.md
│       ├── SaaSAssemblyLineProtocol.md
│       ├── TargetPackageProtocol.md
│       └── README.md
│
├── .claude/                        # Claude Code configuration
│   └── hooks/
│       └── session-start.sh        # Session initialization hook
│
├── .env.example                    # Basic environment template
├── .env.developer.example          # Developer mode settings
├── .env.production.example         # Production configuration
├── .env.self-hosted.example        # Self-hosted deployment
│
├── .gitignore                      # Git exclusions
├── .pre-commit-config.yaml         # Code quality hooks
├── .secrets.baseline               # Secrets detection baseline
│
├── pyproject.toml                  # Python project configuration
│   │                              # - Ruff settings
│   │                              # - MyPy configuration
│   │                              # - Pytest markers
│   │                              # - Bandit security rules
│   └─ requirements-dev.txt         # Development tools
│
├── docker-compose.yml              # Multi-container orchestration
├── Makefile                        # Unix/Linux automation
├── dev.ps1                         # Windows PowerShell automation
│
├── start.sh / start.bat            # Quick start scripts
├── stop.sh / stop.bat              # Stop all services
├── status.sh / status.bat          # Service status
├── logs.sh / logs.bat              # Log viewer
│
├── validate_setup.sh               # Setup verification
├── validate_setup.py               # Python setup check
│
├── test_workflow.py                # Workflow testing utility
│
├── CONTRIBUTING.md                 # Contribution guidelines
├── README.md                        # Main project documentation
├── QUICKSTART.md                   # Quick start guide
├── QUICK_REFERENCE.md              # API reference
├── LICENSE                         # MIT License
│
└── Additional Documentation:
    ├── WORKFLOW_ARCHITECTURE.md    # Workflow system design
    ├── WORKFLOW_LIBRARY_GUIDE.md   # Using workflow library
    ├── IMPLEMENTATION_SUMMARY.md   # Feature summaries
    ├── USER_GUIDE.md               # User documentation
    ├── VISUAL_WALKTHROUGH.md       # UI walkthrough
    ├── DOCKER_TESTING_GUIDE.md     # Docker testing
    ├── ERROR_HANDLING_IMPROVEMENTS.md
    ├── COMFYUI_QUICK_START.md
    ├── COMFYUI_SETUP_GUIDE.md
    ├── WINDOWS_SETUP.md            # Windows-specific setup
    ├── AUTOMATION_GUIDE.md         # Automation tools guide
    ├── TEST_RESULTS.md             # Test documentation
    └── VIDEO_FOUNDRY_README.md     # Legacy readme
```

---

## Backend Structure

### API Routes (`/backend/api`)
The backend exposes RESTful endpoints through FastAPI routers:

#### Projects Router (`projects.py`)
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects (paginated)
- `GET /api/projects/{project_id}` - Get project details
- `PUT /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project

#### Segments Router (`segments.py`)
- `POST /api/segments` - Create video segment
- `GET /api/projects/{project_id}/segments` - List segments
- `GET /api/segments/{segment_id}` - Get segment details
- `PUT /api/segments/{segment_id}` - Update segment
- `DELETE /api/segments/{segment_id}` - Delete segment

#### Render Router (`render.py`)
- `POST /api/render` - Start render job
- `GET /api/render/{job_id}` - Get job status
- `GET /api/render/project/{project_id}` - List jobs for project
- `POST /api/render/{job_id}/cancel` - Cancel job
- WebSocket: `/ws/render/{job_id}` - Real-time progress updates

#### Workflows Router (`workflows.py`)
- `POST /api/workflows` - Create workflow template
- `GET /api/workflows` - List workflows (with filters)
- `GET /api/workflows/{workflow_id}` - Get workflow
- `PUT /api/workflows/{workflow_id}` - Update workflow
- `DELETE /api/workflows/{workflow_id}` - Delete workflow
- `GET /api/workflows/by-name/{name}` - Find by name
- `GET /api/workflows/categories/list` - List categories

#### Health Router (`health.py`)
- `GET /health` - General health check
- `GET /api/health` - Detailed service status
- Includes checks for: Database, Redis, RabbitMQ, ComfyUI

### Models (`/backend/models`)

**Base Model** (`base.py`)
- Base SQLAlchemy model with common patterns
- TimestampMixin: Adds `created_at` and `updated_at`

**Project** (`project.py`)
```python
class Project(Base, TimestampMixin):
    id: UUID (primary key)
    user_id: UUID (foreign key → users)
    name: String
    description: Text
    segments: Relationship[List[Segment]]
    render_jobs: Relationship[List[RenderJob]]
```

**Segment** (`segment.py`)
```python
class Segment(Base, TimestampMixin):
    id: UUID (primary key)
    project_id: UUID (foreign key → projects)
    order_index: Integer
    prompt: Text
    model_type: String (enum: comfyui, runway, stability)
    model_params: JSON (flexible config)
    status: String (enum: pending, processing, completed, failed)
    output_url: String (nullable)
```

**RenderJob** (`render_job.py`)
- Tracks complete render operations
- Status progression: queued → processing → completed/failed
- Progress percentage via WebSocket updates
- Error messages for debugging

**Workflow** (`workflow.py`)
- Workflow templates/library
- Categories for organization
- ComfyUI workflow JSON storage
- User favorites tracking

**User** (`user.py`)
- Basic user model for future auth expansion
- Currently development-focused

### Schemas (`/backend/schemas`)
Pydantic models for request/response validation:

- `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`
- `SegmentCreate`, `SegmentUpdate`, `SegmentResponse`
- `RenderJobResponse`, `RenderJobStatusUpdate`
- `WorkflowCreate`, `WorkflowUpdate`, `WorkflowResponse`

### Services (`/backend/services`)

**Redis Client** (`redis_client.py`)
- Session management
- Caching layer for frequent queries
- Real-time progress tracking

**S3 Client** (`s3_client.py`)
- Abstraction for cloud storage (AWS S3 or compatible)
- Video upload/download
- URL generation for streaming

**RabbitMQ Client** (`rabbitmq_client.py`)
- Task queue interface
- Segment generation queue
- Video composition queue
- Message acknowledgment handling

**Orchestrator** (`orchestrator.py`)
- Business logic for render job management
- Distributes work to RabbitMQ queues
- Aggregates results from workers
- Manages job lifecycle

### Configuration (`/backend/config`)

**Settings** (`settings.py`)
```python
class Settings(BaseSettings):
    # Application
    app_name: str = "Video Foundry"
    environment: str = "development"
    debug: bool = True
    secret_key: str  # Change in production!
    
    # Database
    database_url: str  # PostgreSQL connection
    
    # Cache & Queue
    redis_url: str
    rabbitmq_url: str
    
    # Storage
    s3_bucket: str
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    
    # AI Services
    runway_api_key: Optional[str]
    stability_api_key: Optional[str]
    comfyui_url: str
    
    # Web
    cors_origins: List[str]
```

---

## Frontend Structure

### Application Entry (`src/App.tsx`)
- Main route configuration
- Global state provider setup
- Error boundary implementation

### API Layer (`src/api`)

**Client** (`client.ts`)
```typescript
// Configured Axios instance
// Base URL, headers, interceptors
// Error handling middleware
```

**Projects** (`projects.ts`)
```typescript
export async function getProjects(): Promise<Project[]>
export async function getProject(id: string): Promise<Project>
export async function createProject(data: ProjectCreate): Promise<Project>
export async function updateProject(id: string, data: ProjectUpdate): Promise<Project>
export async function deleteProject(id: string): Promise<void>
```

**Workflows** (`workflows.ts`)
```typescript
export async function getWorkflows(filters?: WorkflowFilters): Promise<Workflow[]>
export async function getWorkflow(id: string): Promise<Workflow>
export async function createWorkflow(data: WorkflowCreate): Promise<Workflow>
export async function updateWorkflow(id: string, data: WorkflowUpdate): Promise<Workflow>
export async function deleteWorkflow(id: string): Promise<void>
export async function getCategories(): Promise<string[]>
```

### Components (`src/components`)

**Header** (`Header.tsx`)
- Navigation menu
- Logo and branding
- User profile (future)

**VideoPlayer** (`VideoPlayer.tsx`)
- HTML5 video element
- Playback controls
- Progress tracking

**VideoModal** (`VideoModal.tsx`)
- Modal dialog for video display
- Responsive design
- Close/download actions

**ComfyUIStatus** (`ComfyUIStatus.tsx`)
- Health indicator component
- Real-time status from WebSocket

### Features (`src/features`)

**Dashboard** (`features/dashboard/Dashboard.tsx`)
- Overview of recent projects
- Quick action buttons
- Statistics display

**Projects** (`features/projects/ProjectList.tsx`)
- List all projects
- Create/edit/delete actions
- Sorting and filtering

**Timeline** (`features/timeline/`)

*TimelineEditor.tsx*
- Main editing interface
- Visual timeline representation
- Segment arrangement
- Drag-and-drop reordering

*SegmentCard.tsx*
- Individual segment display
- Prompt editing
- Model selection
- Status indicators

**Workflows** (`features/workflows/WorkflowLibrary.tsx`)
- Browse workflow templates
- Filter by category
- Copy/use workflows
- Save project as workflow

### State Management (`src/store`)

**useProjectStore** (`useProjectStore.ts`)
- Zustand store
- Current project state
- Segment list management
- Render job tracking
- UI state (modals, selections)

```typescript
interface ProjectStore {
  // State
  currentProject: Project | null
  segments: Segment[]
  renderJob: RenderJob | null
  isLoading: boolean
  
  // Actions
  setCurrentProject(project: Project): void
  addSegment(segment: Segment): void
  updateSegment(id: string, data: Partial<Segment>): void
  deleteSegment(id: string): void
  startRender(): Promise<void>
  cancelRender(): Promise<void>
}
```

### Utilities (`src/utils`)

**Error Messages** (`errorMessages.ts`)
- User-friendly error mapping
- Error code to message translation
- Retry suggestions

### Styling
- Global styles in `index.css`
- TailwindCSS utility classes throughout
- Component-level CSS modules (as needed)

---

## Development Workflows

### Build & Execution

#### Local Development (All Systems)
```bash
# Copy environment file
cp .env.developer.example .env

# Start all services with Docker
make up           # Unix/Linux/Mac
.\dev.ps1 up      # Windows PowerShell

# Services accessible at:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
# ComfyUI: http://localhost:8188
```

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev  # Starts dev server with hot reload
```

#### Worker Development
```bash
cd workers/ai_worker
pip install -r requirements.txt
python worker.py  # Connects to RabbitMQ queue
```

### Database Migrations

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add new field"

# Apply pending migrations
docker-compose exec backend alembic upgrade head

# Rollback last migration
docker-compose exec backend alembic downgrade -1
```

### Code Quality

#### Formatting
```bash
# Format Python code
ruff format backend/ workers/ tests/

# Format frontend code
cd frontend && npm run format

# Or use automated fixes
make format
.\dev.ps1 format
```

#### Linting
```bash
# Lint Python
ruff check backend/ workers/ tests/ --fix

# Lint frontend
cd frontend && npm run lint

# Run all checks
make lint
.\dev.ps1 lint
```

#### Type Checking
```bash
# Check Python types
mypy backend/ workers/ --ignore-missing-imports
```

#### Security Scanning
```bash
# Python security
bandit -c pyproject.toml -r backend/ workers/

# Dependency vulnerabilities
safety check

# Secrets detection
detect-secrets scan
```

### Testing

#### Run All Tests
```bash
make test
.\dev.ps1 test

# Or with coverage
make test-cov
cd tests && pytest --cov=../backend --cov-report=html
```

#### Test Categories
```bash
# Unit tests only
make test-unit
pytest -v -m "not integration and not e2e"

# Integration tests
make test-integration
pytest -v -m integration

# End-to-end tests
make test-e2e
pytest -v tests/e2e/

# Frontend tests
cd frontend && npm test
```

### Pre-commit Hooks

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Skip specific hooks
SKIP=bandit,mypy git commit -m "message"
```

### Docker Operations

```bash
# Build all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# View service logs
docker-compose logs -f backend

# Scale AI workers
docker-compose up -d --scale ai_worker=4

# Interactive shell in container
docker-compose exec backend /bin/bash

# Health check
docker-compose ps
curl http://localhost:8000/health
```

---

## Building and Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── e2e/
│   └── test_timeline_workflow.py  # End-to-end workflow tests
└── requirements.txt         # Test dependencies
```

### Test Markers (pytest)
```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.e2e            # End-to-end tests
@pytest.mark.slow           # Performance-sensitive tests
```

### Running Tests
```bash
# All tests
cd tests && pytest -v

# Specific marker
pytest -v -m "unit"
pytest -v -m "not slow"

# With coverage
pytest --cov=../backend --cov-report=html

# Watch mode (requires pytest-watch)
ptw

# Specific file
pytest tests/e2e/test_timeline_workflow.py -v
```

### Key Testing Dependencies
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-xdist**: Parallel execution
- **factory-boy**: Test data generation
- **faker**: Fake data generation
- **responses**: HTTP mocking

---

## Configuration Management

### Environment Variables

#### Developer Mode (`.env.developer.example`)
```bash
JYNCO_EXECUTION_MODE=developer
DATABASE_URL=postgresql://postgres:password@localhost:5432/videofoundry
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./videos
SECRET_KEY=dev-secret-key-change-me
ENVIRONMENT=development
DEBUG=true
COMFYUI_URL=http://localhost:8188
```

#### Production Mode (`.env.production.example`)
```bash
JYNCO_EXECUTION_MODE=production
# All services require proper URLs and credentials
# Secrets must come from vault, not .env file
ENABLE_DATABASE_RLS=true
ENABLE_AUDIT_LOGGING=true
WORKFLOW_VETTING_STRICT=true
```

#### Self-Hosted (`.env.self-hosted.example`)
```bash
JYNCO_EXECUTION_MODE=self-hosted-production
STORAGE_TYPE=local  # or s3 for MinIO
# Similar to production but with local storage option
```

### Configuration Priority
1. Environment variables
2. `.env` file
3. Default values in `settings.py`

### Service Configuration

**docker-compose.yml**
- Defines all services and their relationships
- Health checks for all services
- Volume mounts for persistence
- Environment variable passing
- GPU support (commented for easy enabling)

---

## Code Organization Patterns

### Backend Patterns

#### 1. **Repository Pattern** (Models + Services)
```python
# models/project.py - Data layer
class Project(Base):
    id: UUID
    name: str

# services/orchestrator.py - Business logic
def create_render_job(project_id):
    # Validation, processing, queue submission
```

#### 2. **Strategy Pattern** (Model Adapters)
```python
# adapters/base.py
class VideoModelInterface(ABC):
    async def initiate_generation(...) -> str
    async def get_generation_status(...) -> GenerationResult

# adapters/comfyui.py, runway.py, stability.py
# Each implements the interface
```

#### 3. **Dependency Injection**
```python
@router.get("/projects")
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # FastAPI provides dependencies via Depends()
```

#### 4. **Async/Await Throughout**
```python
async def initiate_generation(self, prompt: str, params: dict) -> str:
    """Non-blocking I/O for external API calls"""
```

### Frontend Patterns

#### 1. **Component Composition**
```typescript
// Small, focused components
<TimelineEditor>
  <SegmentCard />
  <SegmentCard />
  <SegmentCard />
</TimelineEditor>
```

#### 2. **Zustand State Management**
```typescript
// Centralized, minimal store
const useProjectStore = create((set) => ({
  currentProject: null,
  setCurrentProject: (p) => set({ currentProject: p }),
}))

// Usage in components
const { currentProject, setCurrentProject } = useProjectStore()
```

#### 3. **Custom Hooks for API Calls**
```typescript
// Encapsulates API logic
const useProject = (projectId: string) => {
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    getProject(projectId).then(setProject).finally(() => setLoading(false))
  }, [projectId])
  
  return { project, loading }
}
```

#### 4. **Error Handling**
```typescript
try {
  await createProject(data)
} catch (error) {
  const message = getErrorMessage(error)
  // Display user-friendly error
}
```

---

## Key Concepts

### Segments and Projects
- **Project**: Top-level container for a video editing timeline
- **Segment**: Individual video clip within a project, generated separately
- Segments are ordered and rendered in sequence
- Only modified segments are re-rendered (optimization)

### Render Jobs
- Async operations that generate final videos
- Status progression: queued → processing → completed
- Real-time progress via WebSocket
- Can be canceled mid-processing

### Model Adapters
- Pluggable interfaces for different AI services
- Factory pattern for instantiation
- Each adapter handles API-specific logic
- Easy to add new models

### Workflow Templates
- Reusable ComfyUI workflow configurations
- Stored as JSON with metadata
- Organized by category
- Can be copied to projects

### Real-time Updates
- WebSocket connections for progress tracking
- Redis pub/sub for inter-service communication
- Progress percentages sent to frontend
- Connection management for reliability

---

## Common Development Tasks

### Adding a New API Endpoint

1. **Create Pydantic Schema** (`backend/schemas/`)
```python
class NewResourceCreate(BaseModel):
    field1: str
    field2: int
```

2. **Create SQLAlchemy Model** (`backend/models/`)
```python
class NewResource(Base, TimestampMixin):
    __tablename__ = "new_resources"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    # ... other fields
```

3. **Create Router** (`backend/api/new_resource.py`)
```python
router = APIRouter(prefix="/api/new-resources", tags=["new-resources"])

@router.post("/", response_model=NewResourceResponse)
def create_new_resource(data: NewResourceCreate, db: Session = Depends(get_db)):
    # Implementation
    pass
```

4. **Include Router in main.py**
```python
from api import new_resource
app.include_router(new_resource.router)
```

### Adding a New AI Model Adapter

1. **Create Adapter Class** (`workers/ai_worker/adapters/newmodel.py`)
```python
from adapters.base import VideoModelInterface

class NewModelAdapter(VideoModelInterface):
    async def initiate_generation(self, prompt, params) -> str:
        # Call external API
        pass
    
    async def get_generation_status(self, job_id) -> GenerationResult:
        # Check status
        pass
```

2. **Register in Factory** (`workers/ai_worker/adapters/factory.py`)
```python
def get_adapter(model_type):
    if model_type == "newmodel":
        return NewModelAdapter(api_key)
```

3. **Update Segment Model** to support new type

### Adding Frontend Component

1. **Create Component File** (`frontend/src/components/NewComponent.tsx`)
```typescript
interface NewComponentProps {
  data: string
  onAction: (value: string) => void
}

export function NewComponent({ data, onAction }: NewComponentProps) {
  return (
    <div className="...">
      {/* Component JSX */}
    </div>
  )
}
```

2. **Use in Feature**
```typescript
import { NewComponent } from '@/components/NewComponent'

// In feature component
<NewComponent data={...} onAction={...} />
```

### Database Migration

1. **Modify Model** in `backend/models/`

2. **Generate Migration**
```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

3. **Apply Migration**
```bash
docker-compose exec backend alembic upgrade head
```

---

## Deployment

### Development Deployment
```bash
# All-in-one with Docker Compose
make setup       # Sets up and starts
make up          # Just start
```

### Production Deployment

1. **Prepare Configuration**
```bash
cp .env.production.example .env.production
# Edit with production values
```

2. **Build and Push Images**
```bash
docker build -t your-registry/video-foundry-backend backend/
docker build -t your-registry/video-foundry-frontend frontend/
# Push to registry...
```

3. **Deploy Services**
```bash
docker-compose -f docker-compose.yml up -d
```

4. **Configure Reverse Proxy** (NGINX)
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:5173;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /api {
        proxy_pass http://backend;
    }
    
    location / {
        proxy_pass http://frontend;
    }
}
```

5. **Enable SSL/TLS**
```bash
certbot --nginx -d your-domain.com
```

### Scaling Workers

```bash
# Scale AI workers to 4 instances
docker-compose up -d --scale ai_worker=4

# Monitor with Portainer
# Visit http://localhost:9000
```

### Monitoring

- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Portainer Dashboard**: http://localhost:9000
- **API Health**: GET http://localhost:8000/health
- **Service Logs**: `docker-compose logs -f [service-name]`

### Backup & Recovery

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres videofoundry > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres videofoundry < backup.sql

# Backup volumes
docker run --rm -v video_foundry_postgres_data:/data -v $(pwd):/backup \
    ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

---

## Additional Resources

### Documentation Files
- **WORKFLOW_ARCHITECTURE.md** - Deep dive into workflow system
- **CHROMAFRAME_ARCHITECTURE.md** - 2D animation tool specifications
- **SECURITY_PROPOSAL_V3.md** - Complete security architecture
- **COMFYUI_INTEGRATION.md** - ComfyUI setup and configuration
- **USER_GUIDE.md** - End-user focused documentation
- **TROUBLESHOOTING.md** - Common issues and solutions

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)

### Quick Command Reference

```bash
# Start all services
make up

# View logs
make logs

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Database migrations
make db-migrate

# Scale workers
make scale-workers N=4

# Clean up
make clean-all
```

---

## Notes for AI Assistants

### When Making Changes
1. Maintain type hints throughout (Python & TypeScript)
2. Add docstrings to functions
3. Update tests for new features
4. Follow existing code patterns
5. Update CHANGELOG if significant
6. Consider database migration if schema changes
7. Test with all deployment modes (dev, prod, self-hosted)

### Important Code Locations
- **API Routes**: `backend/api/*.py`
- **Database Models**: `backend/models/*.py`
- **Validation Schemas**: `backend/schemas/*.py`
- **Business Logic**: `backend/services/*.py`
- **Worker Logic**: `workers/*/worker.py`
- **AI Adapters**: `workers/ai_worker/adapters/*.py`
- **Frontend Features**: `frontend/src/features/`
- **API Client**: `frontend/src/api/`
- **State Store**: `frontend/src/store/`

### Common Debugging
- Backend logs: `docker-compose logs -f backend`
- Worker logs: `docker-compose logs -f ai_worker`
- Frontend logs: Browser console
- Database: `docker-compose exec postgres psql -U postgres videofoundry`
- Redis: `docker-compose exec redis redis-cli`
- RabbitMQ: http://localhost:15672

### Performance Tips
1. Use Redis for frequently accessed data
2. Index database columns used in WHERE clauses
3. Lazy load relationships in SQLAlchemy
4. Memoize expensive computations
5. Use batch operations where possible
6. Monitor worker queue lengths

---

**Document Version:** 1.0  
**Last Updated:** November 14, 2025  
**Maintained By:** Video Foundry Team
