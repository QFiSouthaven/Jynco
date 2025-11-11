# Video Foundry - Scalable AI Video Generation Pipeline

## Overview

Video Foundry is a timeline-aware, scalable AI video generation system that enables users to create complex multi-segment video projects using AI models like Runway Gen-3 and Stability AI.

## Architecture

### System Components

1. **Web UI (Frontend)**: React SPA with timeline editor for creating multi-segment video projects
2. **Backend API Gateway**: FastAPI-based orchestrator managing project lifecycles and task dispatching
3. **Message Queue (RabbitMQ)**: Decouples API from workers, manages segment generation tasks
4. **AI Worker Service**: Consumes segment tasks and generates videos via AI models
5. **Composition Worker**: Stitches individual segments into final composite videos
6. **Redis**: Tracks real-time status of render jobs and segments
7. **PostgreSQL**: System-of-record for users, projects, segments, and render metadata
8. **AWS S3/Object Storage**: Stores all generated video assets

### Data Model

- **Project**: Top-level entity representing a user's video timeline
- **Segment**: Individual clips within a project (prompt, model params, order, status)
- **RenderJob**: Specific render request for a project, tracks overall progress

### Key Features

- **Timeline Editor**: Visual interface for creating multi-segment video projects
- **Intelligent Re-rendering**: Only regenerates modified segments
- **Real-time Progress**: WebSocket-based live status updates
- **Multi-Model Support**: Pluggable AI model adapters (Runway, Stability AI, etc.)
- **Scalable Architecture**: Horizontal scaling of worker services

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend/workers development)

### Local Development

```bash
# Start all services
docker-compose up -d

# Backend API will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
# RabbitMQ Management at http://localhost:15672
```

### Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/videofoundry

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# S3/Object Storage
S3_BUCKET=video-foundry-assets
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# AI Model APIs
RUNWAY_API_KEY=your_runway_key
STABILITY_API_KEY=your_stability_key

# Application
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
```

## Project Structure

```
/
├── backend/                # FastAPI Backend
│   ├── api/               # API routes
│   │   ├── projects.py    # Project CRUD
│   │   ├── segments.py    # Segment management
│   │   └── render.py      # Render operations
│   ├── models/            # SQLAlchemy models
│   │   ├── project.py
│   │   ├── segment.py
│   │   └── render_job.py
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── orchestrator.py  # Render orchestration
│   │   └── task_publisher.py
│   └── main.py            # FastAPI app
│
├── workers/
│   ├── ai_worker/         # AI Video Generation
│   │   ├── adapters/      # Model adapters
│   │   │   ├── base.py
│   │   │   ├── runway.py
│   │   │   └── stability.py
│   │   └── worker.py
│   └── composition_worker/  # Video Stitching
│       └── worker.py
│
├── frontend/              # React SPA
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── features/      # Feature modules
│   │   │   ├── timeline/  # Timeline editor
│   │   │   ├── projects/  # Project management
│   │   │   └── dashboard/ # Real-time dashboard
│   │   ├── store/         # State management (Zustand)
│   │   └── api/           # API client
│   └── package.json
│
├── database/
│   └── migrations/        # Alembic migrations
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/               # End-to-end timeline tests
│
└── docs/                  # Additional documentation
```

## API Endpoints

### Projects

- `POST /api/projects` - Create new project
- `GET /api/projects` - List user's projects
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Segments

- `POST /api/projects/{id}/segments` - Add segment to project
- `PUT /api/segments/{id}` - Update segment
- `DELETE /api/segments/{id}` - Remove segment

### Rendering

- `POST /api/projects/{id}/render` - Start render job
- `GET /api/render-jobs/{id}` - Get render job status
- `GET /api/render-jobs/{id}/progress` - Real-time progress (WebSocket)

## Testing

### Run Tests

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests (requires all services running)
pytest tests/e2e

# Specific timeline test
pytest tests/e2e/test_timeline_workflow.py -v
```

### Key E2E Test Scenarios

1. **Multi-segment project creation**: User creates project with multiple segments
2. **Incremental re-render**: User updates one segment, only that segment regenerates
3. **Composition workflow**: All segments complete, composition worker stitches final video
4. **Real-time updates**: WebSocket delivers progress updates to frontend

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Worker Development

```bash
cd workers/ai_worker
python worker.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Production Considerations

1. **Horizontal Scaling**: Scale AI workers based on queue depth
2. **S3 Configuration**: Use CDN for video delivery
3. **Database**: Connection pooling, read replicas for queries
4. **Redis**: Persistent storage for critical job state
5. **Monitoring**: Prometheus metrics, Grafana dashboards
6. **Security**: API rate limiting, authentication, input validation

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Architecture Diagrams

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed system diagrams and data flow.

## Contributing

See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for development guidelines.

## License

[License Type] - See LICENSE file
