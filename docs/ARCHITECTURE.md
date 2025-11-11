# Jynco Architecture Documentation

## Overview

Jynco is a production-ready video generation system that implements a resilient, cost-efficient architecture for AI-powered video creation. The system is designed around a central `storyboard.json` state document and employs specialized agents for different aspects of video generation.

## Core Principles

1. **Domain-First Specialization**: All agents and schemas are designed exclusively for video creation
2. **Orchestration Pattern**: Architect (Coordinator) manages Worker agents
3. **Modular Tool-Wrapping**: Agents wrap best-in-class external AI models and tools
4. **Iterative Generation**: Tight feedback loop for refinement and editing
5. **Operational Excellence**: Built for cost-efficiency, resilience, and scalability

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface / Editor                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Architect Agent                          │
│              (Coordinator & Job Supervisor)                  │
└──┬────────┬────────┬────────┬────────────────────────────┬──┘
   │        │        │        │                            │
   ▼        ▼        ▼        ▼                            ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐              ┌──────────┐
│Story-│ │Motion│ │Render│ │Quarter-│              │ Job Queue│
│board │ │Agent │ │Agent │ │master  │              │ (Priority)│
│Agent │ │      │ │Worker│ │Agent   │              │          │
└──┬───┘ └──┬───┘ └──┬───┘ └───┬────┘              └────┬─────┘
   │        │        │          │                        │
   └────────┴────────┴──────────┴────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
   ┌──────────┐          ┌────────────┐
   │  Cache   │          │ storyboard │
   │(Redis/S3)│          │   .json    │
   └──────────┘          └────────────┘
```

## Agent System

### 1. Architect Agent (Coordinator)

**Responsibilities:**
- Strategic planning of generation pipeline
- Job dispatch to worker agents
- Status monitoring and retry logic
- Priority job submission to queue
- Graceful degradation on failures

**Key Features:**
- Exponential backoff retry (up to 3 attempts)
- Granular error recovery
- Parallel clip generation
- Preview vs. final render prioritization

**Location:** `src/agents/architect_agent.py`

### 2. Storyboard Agent (State Manager)

**Responsibilities:**
- Reading/writing `storyboard.json`
- Status tracking for all clips
- Atomic state updates
- Project state queries

**Key Features:**
- File locking for concurrent access
- Atomic writes (via temp file + rename)
- Real-time status tracking (`pending`, `generating`, `completed`, `failed`)
- Job ID association for monitoring

**Location:** `src/agents/storyboard_agent.py`

### 3. Motion Agent (AI Model Wrapper)

**Responsibilities:**
- Image-to-video generation
- Cache-first strategy implementation
- Deterministic cache key computation
- AI service coordination (Runway, Stability AI, etc.)

**Key Features:**
- SHA-256 cache key from image + prompt
- Automatic cache hit/miss handling
- GPU cost minimization
- Pluggable AI model backends

**Location:** `src/agents/motion_agent.py`

### 4. Render Agent (Video Compositor)

**Responsibilities:**
- FFmpeg video composition
- Timeline clip stitching
- Effect and transition application
- Stateless worker operation

**Key Features:**
- Worker pool scalability
- Quality/speed presets
- Codec configuration
- Filter graph generation

**Location:** `src/agents/render_agent.py`

### 5. Quartermaster Agent (File Manager)

**Responsibilities:**
- Project directory management
- Asset storage and retrieval
- Cache storage coordination
- Cloud storage interface (S3, etc.)

**Key Features:**
- Structured project directories
- Secure path validation
- File deduplication via hashing
- Temporary file cleanup

**Location:** `src/agents/quartermaster_agent.py`

## Infrastructure Components

### Intelligent Caching System

**Purpose:** Minimize GPU compute costs by reusing previously generated clips.

**Implementation:**
- Deterministic cache key: `SHA-256(image_content + motion_prompt + model_version)`
- Multiple backends: Local filesystem, Redis, S3
- Automatic expiration support (TTL)
- Cache hit/miss metrics

**Benefits:**
- Dramatic cost reduction for repeated requests
- Faster response times
- Platform-wide clip sharing

**Location:** `src/infrastructure/cache.py`

### Priority Job Queue

**Purpose:** Ensure responsive UX by prioritizing interactive preview renders over background final exports.

**Implementation:**
- Three priority levels: HIGH (preview), NORMAL (final), LOW (batch)
- Multiple backends: In-memory, RabbitMQ
- Stateless worker design
- Job status tracking

**Benefits:**
- Interactive preview < 5 seconds
- Non-blocking final exports
- Horizontal worker scaling

**Location:** `src/infrastructure/job_queue.py`

## Data Schema

### Storyboard Schema v1.2

The central state document for all video projects.

**Key Enhancements in v1.2:**
- `status` field per clip: `pending`, `generating`, `completed`, `failed`
- `jobId` tracking for monitoring
- `errorMessage` for failed clips
- `cacheKey` for cache integration

**Example:**
```json
{
  "version": "1.2",
  "projectId": "proj_12345",
  "outputSettings": {
    "resolution": {"width": 1920, "height": 1080},
    "fps": 30,
    "codec": "h264"
  },
  "timeline": [
    {
      "clipId": "clip_abc",
      "status": "completed",
      "jobId": "job_motion_xyz",
      "sourceFile": "/projects/proj_12345/clips/clip_abc.mp4",
      "motionPrompt": "camera pans left slowly",
      "cacheKey": "abc123..."
    }
  ]
}
```

**Location:** `src/schemas/storyboard_schema_v1_2.json`

## Resilience & Error Handling

### Granular Error Recovery Protocol

**Problem:** A single agent failure should not corrupt entire project.

**Solution:**

1. **Job Supervision:** Architect stores `jobId` in storyboard
2. **State Tracking:** Storyboard updates status to `generating`
3. **Retry on Failure:** Exponential backoff (3 attempts)
4. **Persistent Failure:** Status set to `failed` with error message
5. **User Recovery:** UI shows failed clip, offers "Retry" or "Edit Prompt"

**Benefits:**
- Project remains intact on failure
- Granular visibility into issues
- User maintains control
- No data loss

### Example Workflow

```
User requests generation
  ↓
Architect dispatches to Motion Agent
  ↓
Storyboard: status = "generating", jobId = "job_motion_123"
  ↓
Motion Agent fails (network timeout)
  ↓
Architect retries with exponential backoff
  ↓
Retry 1: Wait 2s, try again → fails
Retry 2: Wait 4s, try again → fails
Retry 3: Wait 8s, try again → fails
  ↓
Storyboard: status = "failed", errorMessage = "Network timeout"
  ↓
UI displays: ⚠️ Clip generation failed. [Retry] [Edit Prompt]
  ↓
Other clips continue processing ✓
```

## Deployment Considerations

### Development

- In-memory job queue
- Local filesystem cache
- Single-process operation
- Mock AI model responses

### Production

- RabbitMQ or AWS SQS job queue
- Redis cache with S3 storage
- Multi-worker render agents
- Real AI model integration (Runway, Stability AI)
- Horizontal scaling behind load balancer

## Performance Characteristics

| Operation | Development | Production |
|-----------|-------------|------------|
| Cache hit | < 100ms | < 50ms |
| Preview render | 5-10s | 3-5s |
| Final render (1080p, 10s clip) | 30-60s | 15-30s |
| Motion generation (cache miss) | N/A (mock) | 10-20s |

## Security Considerations

- Path validation in Quartermaster (prevent directory traversal)
- Job authentication (future: JWT tokens)
- Rate limiting on Motion Agent (prevent abuse)
- S3 presigned URLs for uploads/downloads
- Cache key collision resistance (SHA-256)

## Scalability

### Horizontal Scaling

- Render Agent workers: Scale to queue depth
- Motion Agent pool: Scale to pending clip count
- Cache: Distributed (Redis + S3)
- Queue: Distributed (RabbitMQ clustering)

### Vertical Scaling

- FFmpeg encoding: GPU acceleration
- Motion AI models: Batch processing
- Storyboard reads: Read replicas

## Monitoring & Observability

**Recommended Metrics:**
- Cache hit rate
- Job queue depth per priority
- Average generation time per clip
- Failure rate per agent
- Render time vs. output duration ratio

**Logging:**
- Structured JSON logging
- Correlation IDs (project ID + job ID)
- Agent-specific log namespaces

## Future Enhancements

1. **Multi-tenant support:** Separate projects by user/org
2. **Webhook notifications:** Alert on job completion
3. **Distributed tracing:** OpenTelemetry integration
4. **Advanced effects:** Custom filter graph builder
5. **AI model fallback:** Automatic failover to backup models
6. **Cost tracking:** Per-project usage analytics

## References

- Design Document: High-Level Design Proposal (Final)
- Storyboard Schema: `src/schemas/storyboard_schema_v1_2.json`
- Agent Documentation: `src/agents/`
- Infrastructure: `src/infrastructure/`
