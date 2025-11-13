# Workflow Library System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────┐         ┌──────────────────────┐        │
│  │  Header           │         │  Timeline Editor      │        │
│  │  - Projects       │         │  ┌─────────────────┐ │        │
│  │  - Workflows ◄────┼────────►│  │ Add Segment     │ │        │
│  │  - Dashboard      │         │  │ ┌─────────────┐ │ │        │
│  └───────────────────┘         │  │ │ Workflow    │ │ │        │
│           │                     │  │ │ Selector    │ │ │        │
│           │                     │  │ └─────────────┘ │ │        │
│           ▼                     │  │ ┌─────────────┐ │ │        │
│  ┌───────────────────┐         │  │ │ Save as     │ │ │        │
│  │ WorkflowLibrary   │         │  │ │ Workflow    │ │ │        │
│  │                   │         │  │ └─────────────┘ │ │        │
│  │ ┌───────────────┐ │         │  └─────────────────┘ │        │
│  │ │ Filter        │ │         └──────────────────────┘        │
│  │ └───────────────┘ │                                          │
│  │ ┌───────────────┐ │                                          │
│  │ │ Workflow Grid │ │                                          │
│  │ │ - Copy        │ │                                          │
│  │ │ - Download    │ │                                          │
│  │ │ - Delete      │ │                                          │
│  │ └───────────────┘ │                                          │
│  └───────────────────┘                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Backend API                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI Router: /api/workflows/                           │ │
│  │                                                             │ │
│  │  GET    /                    → List workflows             │ │
│  │  GET    /{id}                → Get by ID                   │ │
│  │  GET    /by-name/{name}      → Get by name                │ │
│  │  POST   /                    → Create workflow            │ │
│  │  PUT    /{id}                → Update workflow            │ │
│  │  DELETE /{id}                → Delete workflow            │ │
│  │  GET    /categories/list     → List categories            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                              │ SQLAlchemy ORM                    │
│                              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Pydantic Schemas                                          │ │
│  │  - WorkflowCreate    (validation)                          │ │
│  │  - WorkflowUpdate    (validation)                          │ │
│  │  - WorkflowResponse  (serialization)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  SQLAlchemy Model: Workflow                                │ │
│  │                                                             │ │
│  │  - id: UUID (PK)                                           │ │
│  │  - user_id: UUID (FK → users)                              │ │
│  │  - name: String(255)                                       │ │
│  │  - description: Text                                       │ │
│  │  - category: String(100) [indexed]                         │ │
│  │  - workflow_json: JSON                                     │ │
│  │  - is_default: Boolean [indexed]                           │ │
│  │  - created_at: DateTime                                    │ │
│  │  - updated_at: DateTime                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Table: workflows                                                │
│  ┌──────────┬──────────┬──────────┬─────────────┐              │
│  │ id (PK)  │ user_id  │ name     │ description │              │
│  ├──────────┼──────────┼──────────┼─────────────┤              │
│  │ UUID     │ UUID     │ String   │ Text        │              │
│  └──────────┴──────────┴──────────┴─────────────┘              │
│  ┌──────────┬───────────────┬────────────┬──────────────┐      │
│  │ category │ workflow_json │ is_default │ created_at   │      │
│  ├──────────┼───────────────┼────────────┼──────────────┤      │
│  │ String   │ JSON          │ Boolean    │ DateTime     │      │
│  └──────────┴───────────────┴────────────┴──────────────┘      │
│                                                                   │
│  Indexes:                                                        │
│  - idx_workflows_user_id    (user_id)                           │
│  - idx_workflows_category   (category)                          │
│  - idx_workflows_is_default (is_default)                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Initialization
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   Database Initialization                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  On Startup: create_default_workflows()                          │
│                                                                   │
│  1. Check if defaults exist                                      │
│  2. Load /workflows/*.json files                                │
│  3. Insert default workflows:                                    │
│     - Text to Video (Basic)                                      │
│     - Image to Video (Basic)                                     │
│  4. Mark as is_default=True                                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Loading Workflow in Timeline Editor

```
User Action: Select workflow from dropdown
         │
         ▼
┌─────────────────────┐
│ TimelineEditor      │
│ handleWorkflowSelect│
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Find in local state │
│ (React Query cache) │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Set selectedWorkflow│
│ Populate JSON       │
└─────────────────────┘
         │
         ▼
User sees workflow JSON in textarea
```

### 2. Saving Custom Workflow

```
User Action: Click "Save as Workflow"
         │
         ▼
┌─────────────────────┐
│ Show save modal     │
│ - Name input        │
│ - Description input │
│ - Category select   │
└─────────────────────┘
         │
         ▼
User fills form and clicks "Save"
         │
         ▼
┌─────────────────────┐
│ Parse workflow JSON │
│ Validate inputs     │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ POST /api/workflows/│
│ { name, desc, cat,  │
│   workflow_json }   │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Backend validates   │
│ via Pydantic        │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Insert into DB      │
│ workflows table     │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Return workflow     │
│ with UUID           │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Update React Query  │
│ cache               │
└─────────────────────┘
         │
         ▼
User sees "Workflow saved successfully!"
```

### 3. Browsing Workflows

```
User navigates to /workflows
         │
         ▼
┌─────────────────────┐
│ WorkflowLibrary     │
│ component loads     │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ useQuery()          │
│ GET /api/workflows/ │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Backend queries DB  │
│ with filters        │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Return workflows    │
│ (defaults + custom) │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Render grid cards   │
│ - Name, description │
│ - Category badge    │
│ - Action buttons    │
└─────────────────────┘
         │
         ▼
User can filter by category
User can click to see details
User can copy/download/delete
```

## Component Hierarchy

```
App
├── Header
│   ├── Logo & Title
│   ├── Navigation
│   │   ├── Projects Link
│   │   ├── Workflows Link ← NEW
│   │   └── Dashboard Link
│   └── ComfyUI Status
│
├── Routes
│   ├── / → ProjectList
│   │
│   ├── /projects/:id → TimelineEditor
│   │   ├── Project Header
│   │   ├── Timeline View
│   │   └── Add Segment Modal ← ENHANCED
│   │       ├── Model Selection
│   │       ├── Prompt Input
│   │       ├── Dimension Inputs
│   │       └── ComfyUI Section
│   │           ├── Workflow Selector ← NEW
│   │           ├── Workflow JSON Textarea
│   │           └── Save as Workflow Button ← NEW
│   │
│   ├── /workflows → WorkflowLibrary ← NEW
│   │   ├── Page Header
│   │   ├── Category Filter ← NEW
│   │   ├── Workflow Grid ← NEW
│   │   │   └── Workflow Cards
│   │   │       ├── Name & Description
│   │   │       ├── Category Badge
│   │   │       ├── Default Badge
│   │   │       └── Action Buttons
│   │   └── Detail Modal ← NEW
│   │       ├── Full Details
│   │       ├── JSON Display
│   │       └── Actions
│   │
│   └── /dashboard → Dashboard
│
└── Modals
    ├── Add Segment Modal (enhanced)
    └── Save Workflow Modal ← NEW
        ├── Name Input
        ├── Description Input
        └── Category Select
```

## API Request/Response Examples

### List Workflows
```http
GET /api/workflows/?category=text-to-video&include_defaults=true

Response:
[
  {
    "id": "uuid-1",
    "user_id": "uuid-user",
    "name": "Text to Video (Basic)",
    "description": "Basic text-to-video workflow...",
    "category": "text-to-video",
    "workflow_json": { ... },
    "is_default": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Workflow
```http
POST /api/workflows/
Content-Type: application/json

{
  "name": "My Custom Workflow",
  "description": "High-res animation workflow",
  "category": "custom",
  "workflow_json": {
    "1": { "class_type": "CheckpointLoader", ... }
  }
}

Response:
{
  "id": "uuid-new",
  "user_id": "uuid-user",
  "name": "My Custom Workflow",
  "description": "High-res animation workflow",
  "category": "custom",
  "workflow_json": { ... },
  "is_default": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Delete Workflow
```http
DELETE /api/workflows/{workflow-id}

Success Response: 204 No Content

Error Response (if default):
{
  "detail": "Cannot delete default workflows"
}
```

## File Dependencies

```
Backend Dependencies:
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Pydantic (validation)
- PostgreSQL (database)

Frontend Dependencies:
- React (UI framework)
- TypeScript (type safety)
- React Router (routing)
- TanStack Query (data fetching)
- Axios (HTTP client)
- React Icons (icons)
- Tailwind CSS (styling)
```

## Database Relationships

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK)         │◄────┐
│ email           │     │
│ username        │     │
│ ...             │     │
└─────────────────┘     │
                        │ FK
                        │
┌─────────────────┐     │
│   workflows     │     │
│─────────────────│     │
│ id (PK)         │     │
│ user_id (FK)    │─────┘
│ name            │
│ description     │
│ category        │
│ workflow_json   │
│ is_default      │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Security Considerations

1. **User Ownership**: All workflows tied to user_id for future multi-tenant support
2. **Default Protection**: is_default flag prevents deletion/modification of system workflows
3. **JSON Validation**: Pydantic ensures valid JSON structure
4. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
5. **Input Validation**: All inputs validated before DB operations
6. **Error Handling**: Proper HTTP status codes and error messages

## Performance Optimizations

1. **Database Indexes**: Fast filtering on user_id, category, is_default
2. **React Query Caching**: Reduces redundant API calls
3. **Lazy Loading**: Workflow details loaded on demand
4. **Efficient Queries**: Only fetch necessary fields
5. **JSON Storage**: Direct storage avoids expensive normalization
6. **Connection Pooling**: Backend uses connection pool for DB

---

This architecture provides a scalable, maintainable, and user-friendly workflow library system.
