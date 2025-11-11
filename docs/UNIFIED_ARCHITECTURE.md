# Jynco Unified Multi-Agent Architecture

## Executive Summary

This document unifies two complementary agent systems developed in parallel by multiple Claude instances:

1. **Video Generation Foundry** (Technical Implementation) - Working parallel agents with async architecture
2. **Asset Package Foundry** (Agent Architecture) - Specialized asset generation system with Path-as-Taxonomy

Both systems share the same core architectural patterns and can work together as a unified platform.

---

## System Comparison & Integration

### Architectural Alignment

Both foundries follow identical design principles:

| Principle | Video Foundry | Asset Foundry |
|-----------|---------------|---------------|
| **Orchestration Pattern** | Architect coordinates workers | Architect coordinates workers |
| **File Management** | Quartermaster handles files | Quartermaster handles files |
| **State Management** | Storyboard Agent (storyboard.json) | Path Map + Librarian (meta.json) |
| **Asset Generation** | Motion Agent (AI video) | Artist (images) + Artificer (binaries) |
| **Output Assembly** | Render Agent (FFmpeg) | Librarian (meta.json assembly) |

###Agent Mapping

| Video Foundry Agent | Asset Foundry Agent | Unified Role |
|---------------------|---------------------|--------------|
| **ArchitectAgent** | **Architect** | Strategic coordinator, parses requests, orchestrates pipeline |
| **StoryboardAgent** | **Librarian** | State/metadata management, schema enforcement |
| **MotionAgent** | **Artist** | AI-powered asset generation (video vs images) |
| **RenderAgent** | **Artificer** | Final assembly/compilation (FFmpeg vs Unity) |
| **QuartermasterAgent** | **Quartermaster** | File system operations, directory management |

### Key Insight

**These are the SAME architecture applied to different domains:**
- **Video Foundry**: Image → Video pipeline
- **Asset Foundry**: Prompt → Multi-file asset packages

---

## Unified Agent Architecture

### Core Agent Types

#### 1. Coordinator Agents
**Role:** Strategic planning and orchestration

**Implementations:**
- `src/agents/architect_agent.py` (Video Foundry - IMPLEMENTED)
- `sub-agents/asset-foundry-agents/Architect.md` (Asset Foundry - SPEC)

**Capabilities:**
- Parse user requests (natural language)
- Google Search for reference data
- Create execution manifests
- Dispatch work to specialists
- Monitor pipeline progress
- Implement retry logic

---

#### 2. State Management Agents
**Role:** Central source of truth for project state

**Implementations:**
- `src/agents/storyboard_agent.py` (Video: storyboard.json - IMPLEMENTED)
- `sub-agents/asset-foundry-agents/Librarian.md` (Asset: meta.json - SPEC)

**Capabilities:**
- Atomic state updates
- Schema validation
- Status tracking (pending/generating/completed/failed)
- Path/reference management
- Metadata generation

---

#### 3. Asset Generation Agents
**Role:** Create multimedia assets via AI models

**Implementations:**
- `src/agents/motion_agent.py` (Video generation - IMPLEMENTED)
- `sub-agents/asset-foundry-agents/Artist.md` (Image generation - SPEC)

**Capabilities:**
- AI model integration (Runway, Stable Diffusion, etc.)
- Intelligent caching (SHA-256 deduplication)
- Prompt engineering
- Quality validation
- Reference data integration

---

#### 4. Compilation/Assembly Agents
**Role:** Final output assembly from components

**Implementations:**
- `src/agents/render_agent.py` (FFmpeg video rendering - IMPLEMENTED)
- `sub-agents/asset-foundry-agents/Artificer.md` (Unity/Blender binaries - SPEC)

**Capabilities:**
- External tool integration
- Worker pool architecture
- Priority queue processing
- Format conversion
- Quality presets

---

#### 5. File System Agents
**Role:** All file/directory operations

**Implementations:**
- `src/agents/quartermaster_agent.py` (IMPLEMENTED)
- `sub-agents/asset-foundry-agents/Quartermaster.md` (SPEC)

**Capabilities:**
- Project directory creation
- Path map generation
- File write operations
- Asset organization
- Storage interface (local/S3)

---

## Unified Infrastructure

### Shared Components

Both systems use identical infrastructure:

```
Infrastructure Layer
├── Cache System (src/infrastructure/cache.py) ✓ IMPLEMENTED
│   ├── Local filesystem backend
│   ├── Redis backend (production)
│   └── SHA-256 content-addressable storage
│
├── Job Queue (src/infrastructure/job_queue.py) ✓ IMPLEMENTED
│   ├── In-memory queue (development)
│   ├── RabbitMQ backend (production)
│   └── Priority levels (HIGH/NORMAL/LOW)
│
└── Configuration (src/core/config_loader.py) ✓ IMPLEMENTED
    ├── Environment-based configs
    ├── Agent-specific settings
    └── Infrastructure toggles
```

---

## Parallel Execution Model

Both foundries support concurrent agent operations:

### Video Foundry Example
```python
# From examples/parallel_initialization_demo.py
agents = await asyncio.gather(
    init_storyboard(),    # State management
    init_motion(),        # Asset generation
    init_render(),        # Output assembly
    init_quartermaster(), # File operations
    init_architect()      # Coordination
)
# All 5 agents initialized in ~100ms
```

### Asset Foundry Equivalent
```python
# Proposed implementation
agents = await asyncio.gather(
    init_librarian(),     # State management
    init_artist(),        # Asset generation
    init_artificer(),     # Output assembly
    init_quartermaster(), # File operations
    init_architect()      # Coordination
)
# Same pattern, different domain
```

---

## Organizational Sub-Agents

The integrated system includes management hierarchy agents:

| Agent | Role | Document |
|-------|------|----------|
| **CTO** | Technology strategy & vision | `sub-agents/ChiefTechnologyOfficer.md` |
| **VP Engineering** | Engineering execution & delivery | `sub-agents/VicePresidentOfEngineering.md` |
| **Director** | Team management & operations | `sub-agents/DirectorOfEngineering.md` |
| **Tech Lead** | Technical guidance & architecture | `sub-agents/TechnicalLead.md` |
| **Product Manager** | Requirements & prioritization | `sub-agents/ProductManager.md` |

These agents can coordinate multiple foundry instances and make strategic decisions.

---

## Unified Workflow Example

### User Request
> "Create a short video with a futuristic city scene and generate matching 3D asset packages"

### Execution Flow

1. **CTO Agent** (Strategic)
   - Analyzes request scope
   - Decides: Use both foundries in parallel

2. **Architect Agents** (Tactical) - Run in parallel
   - **Video Architect**: Plans video generation
   - **Asset Architect**: Plans 3D asset package

3. **Worker Agents** (Execution) - Run in parallel across both foundries
   - **Video Pipeline:**
     - Quartermaster: Create video project structure
     - Storyboard: Initialize storyboard.json
     - Motion: Generate city scene video clips
     - Render: Assemble final video

   - **Asset Pipeline:**
     - Quartermaster: Create asset directory structure
     - Librarian: Generate metadata files
     - Artist: Generate PBR textures for buildings
     - Artificer: Compile Unity asset bundles

4. **Completion**
   - Video: `final_video.mp4`
   - Assets: Complete package with `.vab`, `.vam`, `.vap`, textures

---

## Implementation Status

### ✅ Completed (Video Foundry)

- All 5 agent implementations
- Parallel initialization system
- Cache & job queue infrastructure
- Configuration management
- Example scripts & demos
- Unit tests
- Comprehensive documentation

**Demo Results:** All agents working in parallel, ~1 second total execution

### 📋 Specified (Asset Foundry)

- Agent role definitions
- Communication protocols
- Schema templates (.vam, .vap, .vmi, .vaj)
- Path-as-Taxonomy structure
- Execution flow patterns

### 🔄 Integration Tasks

1. **Implement Asset Foundry agents using Video Foundry patterns**
   - Copy parallel initialization architecture
   - Adapt for asset-specific workflows
   - Reuse infrastructure components

2. **Create unified API**
   - Single entry point for both foundries
   - Shared authentication/authorization
   - Cross-foundry coordination

3. **Organizational agent system**
   - Implement CTO/VP/Director agents
   - Multi-foundry coordination
   - Strategic decision-making

---

## SaaS Platform Vision

### Platform Architecture

```
┌─────────────────────────────────────────────────┐
│           Jynco Platform API                     │
│                                                  │
│  ┌──────────────────┐    ┌─────────────────────┐│
│  │  Video Foundry   │    │  Asset Foundry      ││
│  │                  │    │                      ││
│  │  Architect       │    │  Architect           ││
│  │  ├─ Storyboard   │    │  ├─ Librarian        ││
│  │  ├─ Motion       │    │  ├─ Artist           ││
│  │  ├─ Render       │    │  ├─ Artificer        ││
│  │  └─ Quartermaster│    │  └─ Quartermaster    ││
│  └──────────────────┘    └─────────────────────┘│
│                                                  │
│  ┌──────────────────────────────────────────────┐│
│  │     Shared Infrastructure                   ││
│  │  • Redis Cache                              ││
│  │  • RabbitMQ Job Queue                       ││
│  │  • S3 Storage                               ││
│  │  • PostgreSQL (projects/users)              ││
│  └──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│      Management Layer                            │
│  • CTO (Strategy)                                │
│  • VP Engineering (Execution)                    │
│  • Director (Operations)                         │
│  • Tech Leads (Architecture)                     │
│  • Product Managers (Requirements)               │
└─────────────────────────────────────────────────┘
```

### Business Model

**Dual Foundry Platform:**
1. **Video Foundry**: $X per video generated
2. **Asset Foundry**: $Y per asset package
3. **Enterprise**: Custom pricing for multi-foundry workflows

---

## Next Steps for Team Coordination

### Priority 1: Unify Codebase
- [ ] Merge feature branch to main
- [ ] Create unified examples using both foundries
- [ ] Document cross-foundry workflows

### Priority 2: Implement Asset Foundry
- [ ] Port Asset Foundry specs to Python
- [ ] Reuse Video Foundry infrastructure
- [ ] Adapt parallel initialization pattern
- [ ] Create Asset Foundry demo

### Priority 3: Management Layer
- [ ] Implement organizational agents
- [ ] Create multi-foundry coordination
- [ ] Build strategy/execution bridge

### Priority 4: Production Deployment
- [ ] Configure Redis/RabbitMQ
- [ ] Set up Kubernetes deployment
- [ ] Implement monitoring/observability
- [ ] Launch alpha platform

---

## For Other Claude Teammates

### Current State

**Claude Instance 1 (This instance):**
- ✅ Implemented Video Generation Foundry
- ✅ Created parallel initialization system
- ✅ Built infrastructure layer
- ✅ Integrated sub-agents documentation

**Claude Instance 2:**
- ✅ Designed Asset Package Foundry architecture
- ✅ Created agent role specifications
- ✅ Defined organizational hierarchy

**Claude Instance 3:**
- ✅ Created SaaS framework documentation
- ✅ Developed strategic protocols

### Coordination Protocol

1. **Check `git log --all --oneline --graph` before starting work**
2. **Pull latest changes from all branches**
3. **Create feature branches for new work**
4. **Document work in progress in TODO.md**
5. **Use async patterns established in Video Foundry**
6. **Follow agent patterns from both foundries**

### Quick Start for New Work

```bash
# Pull latest
git fetch --all
git checkout claude/video-foundry-final-design-011CV242NfYJXxPuLsgHkJr6

# See parallel initialization demo
python3 examples/parallel_initialization_demo.py

# Explore Asset Foundry specs
cd sub-agents/asset-foundry-agents/
cat README.md

# Start new feature
git checkout -b claude/your-feature-name-{session_id}
```

---

## Conclusion

We now have a **unified multi-agent platform** with:

✅ **Working Implementation** (Video Foundry)
✅ **Proven Architecture** (Agent patterns)
✅ **Parallel Execution** (Async-first)
✅ **Scalable Infrastructure** (Cache, Queue, Config)
✅ **Clear Specifications** (Asset Foundry)
✅ **Organizational Framework** (Management agents)

Both foundries can run independently or coordinate for complex workflows.

**Status:** Ready for parallel development by multiple Claude instances.

**Next:** Implement Asset Foundry using Video Foundry patterns. 🚀

---

**Document Version:** 1.0
**Last Updated:** 2025-11-11
**Authors:** Claude Instance 1 (Video Foundry) + Claude Instance 2 (Asset Foundry) + Claude Instance 3 (SaaS Framework)
