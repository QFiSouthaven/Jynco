# Workflow Library Management System

## Overview

The Workflow Library Management System allows users to save, browse, and reuse ComfyUI workflows easily. This feature makes it simple for users to discover pre-configured workflows and save their own custom configurations for future use.

## Features Implemented

### Backend (Python/FastAPI)

1. **Database Model** (`/home/user/Jynco/backend/models/workflow.py`)
   - Stores workflow metadata and JSON configuration
   - Fields: name, description, category, workflow_json, is_default, user_id
   - Supports both user-created and system-default workflows

2. **API Endpoints** (`/home/user/Jynco/backend/api/workflows.py`)
   - `GET /api/workflows/` - List all workflows (with optional category filter)
   - `GET /api/workflows/{id}` - Get specific workflow by ID
   - `GET /api/workflows/by-name/{name}` - Get workflow by name
   - `POST /api/workflows/` - Save a new custom workflow
   - `PUT /api/workflows/{id}` - Update an existing workflow
   - `DELETE /api/workflows/{id}` - Delete a custom workflow
   - `GET /api/workflows/categories/list` - List all categories

3. **Pydantic Schemas** (`/home/user/Jynco/backend/schemas/workflow.py`)
   - WorkflowCreate - For creating new workflows
   - WorkflowUpdate - For updating workflows
   - WorkflowResponse - For API responses

4. **Database Initialization** (`/home/user/Jynco/backend/config/database.py`)
   - Automatically populates default workflows on startup
   - Loads `text-to-video-basic.json` and `image-to-video-basic.json`
   - Creates workflows with proper metadata and categories

### Frontend (React/TypeScript)

1. **API Client** (`/home/user/Jynco/frontend/src/api/workflows.ts`)
   - TypeScript interfaces for Workflow data
   - API methods for all CRUD operations
   - Category filtering support

2. **TimelineEditor Updates** (`/home/user/Jynco/frontend/src/features/timeline/TimelineEditor.tsx`)
   - **Workflow Selector Dropdown**: Browse and select from library
   - **Description Display**: Shows workflow details on selection
   - **Auto-populate JSON**: Loads selected workflow into textarea
   - **Save as Workflow Button**: Save current JSON as a new workflow
   - **Save Workflow Modal**: Collect name, description, and category

3. **WorkflowLibrary Component** (`/home/user/Jynco/frontend/src/features/workflows/WorkflowLibrary.tsx`)
   - Browse all available workflows in a grid layout
   - Category filtering
   - Workflow cards showing name, description, category, date
   - Actions: Copy JSON, Download JSON, Delete (custom only)
   - Detailed workflow view modal
   - Default workflows are clearly marked and protected

4. **Navigation** (`/home/user/Jynco/frontend/src/App.tsx`, `/home/user/Jynco/frontend/src/components/Header.tsx`)
   - Added `/workflows` route
   - Added "Workflows" navigation link in header

## How to Use

### For End Users

#### Browsing Workflows

1. Click "Workflows" in the navigation menu
2. Browse available workflows in the grid view
3. Use the category filter to narrow down options
4. Click on a workflow card to see full details
5. Use "Copy JSON" or "Download JSON" to export workflows

#### Using Workflows in Timeline Editor

1. Create a new project or open an existing one
2. Click "Add Segment"
3. Select "ComfyUI" as the AI Model
4. In the "Load from Workflow Library" dropdown, select a workflow
5. The workflow JSON will automatically populate the textarea
6. Modify if needed, or use as-is
7. Complete the segment creation

#### Saving Custom Workflows

1. In the TimelineEditor, create or paste a ComfyUI workflow JSON
2. Click the "Save as Workflow" button
3. Enter a name, description (optional), and category
4. Click "Save Workflow"
5. Your workflow is now available in the library for reuse

#### Managing Workflows

- **View**: Navigate to Workflows page to see all workflows
- **Copy**: Click "Copy" button to copy JSON to clipboard
- **Download**: Click "Download" to save JSON file locally
- **Delete**: Click trash icon to delete custom workflows (defaults cannot be deleted)

### For Developers

#### Database Schema

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    workflow_json JSON NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_category ON workflows(category);
CREATE INDEX idx_workflows_is_default ON workflows(is_default);
```

#### Adding New Default Workflows

1. Add workflow JSON file to `/home/user/Jynco/workflows/`
2. Update `create_default_workflows()` in `/home/user/Jynco/backend/config/database.py`
3. Add entry to `default_workflows` list:
```python
{
    "name": "Workflow Name",
    "description": "Description of what it does",
    "category": "category-name",
    "file": "filename.json"
}
```
4. Restart the backend - workflows will be auto-populated

#### Workflow Categories

Current categories:
- `text-to-video` - Generate video from text prompts
- `image-to-video` - Generate video from images
- `video-to-video` - Transform existing videos
- `custom` - User-defined workflows

Add more categories as needed in the UI and backend.

## API Examples

### List All Workflows
```bash
curl http://localhost:8000/api/workflows/
```

### Get Workflow by Category
```bash
curl http://localhost:8000/api/workflows/?category=text-to-video
```

### Create New Workflow
```bash
curl -X POST http://localhost:8000/api/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Workflow",
    "description": "A specialized workflow for...",
    "category": "custom",
    "workflow_json": {...}
  }'
```

### Delete Workflow
```bash
curl -X DELETE http://localhost:8000/api/workflows/{workflow_id}
```

## File Structure

```
/home/user/Jynco/
├── backend/
│   ├── api/
│   │   └── workflows.py          # API routes
│   ├── models/
│   │   └── workflow.py           # Database model
│   ├── schemas/
│   │   └── workflow.py           # Pydantic schemas
│   └── config/
│       └── database.py           # DB init + default workflows
├── frontend/
│   └── src/
│       ├── api/
│       │   └── workflows.ts      # TypeScript API client
│       ├── features/
│       │   ├── timeline/
│       │   │   └── TimelineEditor.tsx  # Updated with workflow selector
│       │   └── workflows/
│       │       └── WorkflowLibrary.tsx # Workflow browser component
│       ├── components/
│       │   └── Header.tsx        # Updated with Workflows link
│       └── App.tsx               # Added /workflows route
└── workflows/
    ├── text-to-video-basic.json  # Default workflow 1
    └── image-to-video-basic.json # Default workflow 2
```

## Key Design Decisions

1. **Database Storage**: Workflows are stored in the database (not just files) for better querying, filtering, and user management.

2. **Default Workflows**: System workflows are marked with `is_default=True` and cannot be deleted or modified by users.

3. **User Ownership**: All workflows have a user_id, allowing for future multi-user support and personal workflow libraries.

4. **JSON Flexibility**: Workflow JSON is stored as-is, allowing any ComfyUI workflow structure without schema constraints.

5. **Category System**: Simple string-based categories make it easy to organize and filter workflows.

6. **Non-intrusive UX**: Workflow selection is optional - users can still paste JSON directly if preferred.

## Testing

After restarting the backend, verify:

1. Database table created: `SELECT * FROM workflows;`
2. Default workflows populated (should see 2 entries)
3. Frontend can fetch workflows: Check browser network tab
4. Can save custom workflow from TimelineEditor
5. Can browse workflows in WorkflowLibrary
6. Can delete custom workflows (not defaults)

## Future Enhancements

- Workflow templates with variable substitution
- Workflow validation (check for required nodes)
- Workflow versioning
- Community workflow sharing
- Workflow tags for better discovery
- Workflow thumbnails/previews
- Import/export workflow collections
- Workflow usage statistics

## Troubleshooting

### Default workflows not appearing
- Check backend logs for database errors
- Verify workflow JSON files exist in `/workflows/`
- Ensure `create_default_workflows()` is called in `init_db()`

### Cannot save workflow
- Check browser console for API errors
- Verify JSON is valid (try JSON.parse() in console)
- Check backend logs for schema validation errors

### Cannot delete workflow
- Ensure workflow is not a default (is_default=False)
- Verify user has permission (check user_id)
- Check backend logs for constraint errors
