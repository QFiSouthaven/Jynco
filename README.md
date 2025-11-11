# Jynco - AI-Powered Multi-Agent Systems

Welcome to the Jynco repository - a collection of sophisticated AI-powered systems and frameworks.

## Systems

### 1. Video Foundry - Scalable AI Video Generation Pipeline

A timeline-aware, production-ready system for generating AI videos with intelligent segment management and composition.

**Key Features:**
- Timeline-based video editor for multi-segment projects
- Intelligent re-rendering (only regenerates modified segments)
- Pluggable AI model adapters (Runway Gen-3, Stability AI, etc.)
- Horizontal scaling with worker services
- Real-time progress tracking via WebSockets
- Automatic video composition with FFMPEG

**Architecture:**
- FastAPI backend with orchestration logic
- React/TypeScript frontend with timeline editor
- RabbitMQ for task queuing
- Redis for real-time state
- PostgreSQL for persistence
- S3 for video storage

📖 **[Full Documentation](./VIDEO_FOUNDRY_README.md)**

**Quick Start:**
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Access the application
# - Frontend UI:     http://localhost:5173
# - Backend API:     http://localhost:8000
# - API Docs:        http://localhost:8000/docs
# - RabbitMQ Console: http://localhost:15672 (guest/guest)
```

**Documentation:**
- 📘 [Quick Start Guide](./QUICKSTART.md) - Get up and running in 5 minutes
- 📖 [User Guide](./USER_GUIDE.md) - Complete guide to creating videos
- 🖼️ [Visual Walkthrough](./VISUAL_WALKTHROUGH.md) - Step-by-step with screenshots
- 🧪 [Test Script](./test_workflow.py) - Automated workflow demonstration

**GPU Acceleration:**
- Configured for NVIDIA GPUs with CUDA support
- 2 parallel AI workers for concurrent segment generation
- Local hardware mode enabled by default (no cloud API keys required)

### 2. Asset Package Foundry

A multi-agent system for generating schema-compliant asset packages from high-level creative prompts.

**Agents:**
- **Architect** - Orchestrator and planner
- **Quartermaster** - File system operations
- **Librarian** - Metadata and schema validation
- **Artist** - Image generation
- **Artificer** - Binary asset generation

📖 **[Documentation](./sub-agents/asset-foundry-agents/README.md)**

## Repository Structure

```
/
├── backend/              # Video Foundry - FastAPI backend
├── frontend/             # Video Foundry - React SPA
├── workers/              # Video Foundry - AI & Composition workers
├── sub-agents/           # Asset Foundry - Agent definitions
├── database/             # Database migrations
├── tests/                # E2E and integration tests
├── docs/                 # Additional documentation
├── docker-compose.yml    # Docker orchestration
└── VIDEO_FOUNDRY_README.md  # Video Foundry detailed docs
```

## Development

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3+

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Run tests**
```bash
# Backend tests
cd tests
pip install -r requirements.txt
pytest -v

# Frontend (optional)
cd frontend
npm install
npm test
```

## Key Technologies

- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Frontend:** React, TypeScript, TailwindCSS, Zustand
- **Queuing:** RabbitMQ
- **Cache:** Redis
- **Database:** PostgreSQL
- **Storage:** AWS S3
- **Video:** FFMPEG
- **AI Models:** Runway Gen-3, Stability AI

## Contributing

Contributions are welcome! Please see individual system documentation for specific guidelines.

## License

[Specify License]

## Contact

For questions or support, please open an issue in this repository.
