# ChromaFrame + Video Foundry Integration Strategy

**Version:** 1.0
**Date:** January 2025
**Status:** Planning

---

## Executive Summary

This document outlines the integration strategy between ChromaFrame (2D animation desktop application) and Video Foundry (AI video generation platform). The goal is to create a seamless workflow where users can create 2D animations in ChromaFrame and enhance them with AI-powered effects in Video Foundry.

---

## 1. Integration Architecture

### 1.1 Hybrid Architecture (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                    ChromaFrame Desktop App                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Animation     │  │  2D Drawing    │  │   Export     │  │
│  │  Editor        │  │  Tools         │  │   Pipeline   │  │
│  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘  │
│           │                   │                   │          │
│           └───────────────────┴───────────────────┘          │
│                              │                                │
└──────────────────────────────┼────────────────────────────────┘
                               │
                               │ Export/Sync
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Video Foundry Cloud Platform                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Backend API (FastAPI)                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Project      │  │ ChromaFrame  │  │ AI           │ │ │
│  │  │ Management   │  │ Integration  │  │ Processing   │ │ │
│  │  │ Service      │  │ Service      │  │ Pipeline     │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │ │
│  └─────────┼──────────────────┼──────────────────┼─────────┘ │
│            │                  │                  │           │
│  ┌─────────┼──────────────────┼──────────────────┼─────────┐ │
│  │         ▼                  ▼                  ▼         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │           Storage Layer (S3/Local)                │  │ │
│  │  │  .cframe Projects │ Rendered Frames │ AI Videos  │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                                │
└──────────────────────────────┼────────────────────────────────┘
                               │
                               │ Stream/Download
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Video Foundry Web Frontend (React)              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Timeline      │  │  AI Effects    │  │   Preview    │  │
│  │  Editor        │  │  Controls      │  │   Player     │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Integration Scenarios

### Scenario 1: Export & Upload

**Workflow:**
1. User creates animation in ChromaFrame
2. Exports project as `.cframe` file
3. Uploads to Video Foundry via web interface
4. Video Foundry extracts frames
5. Applies AI effects (upscaling, style transfer, etc.)
6. Renders final enhanced video

**Implementation:**
```python
# backend/api/chromaframe.py
@router.post("/projects/upload-chromaframe")
async def upload_chromaframe(
    file: UploadFile,
    user: User = Depends(get_current_user)
):
    # Extract .cframe file
    project = ChromaFrameParser.parse(file)

    # Create Video Foundry project
    vf_project = Project(
        user_id=user.id,
        name=project.name,
        source_type="chromaframe"
    )

    # Extract frames as timeline segments
    for scene in project.scenes:
        for layer in scene.layers:
            segment = create_segment_from_layer(layer)
            vf_project.segments.append(segment)

    return {"project_id": vf_project.id}
```

### Scenario 2: Cloud Sync & Collaboration

**Workflow:**
1. User signs into ChromaFrame with Video Foundry account
2. Projects automatically sync to cloud
3. Edit in ChromaFrame or web interface
4. Changes synchronized in real-time
5. Export and enhance in Video Foundry

**Implementation:**
```cpp
// ChromaFrame: services/CloudSyncService.h
class CloudSyncService {
public:
    void syncProject(const Project& project);
    void pullUpdates();
    void pushChanges();
    void enableAutoSync(bool enable);

private:
    HttpClient httpClient_;
    std::string authToken_;
    SyncQueue syncQueue_;
};
```

### Scenario 3: ChromaFrame as Microservice

**Workflow:**
1. Video Foundry web app has "Create 2D Animation" button
2. Launches embedded ChromaFrame viewer (WebAssembly?)
3. User creates basic animation in browser
4. Saved directly to Video Foundry project
5. Enhanced with AI pipeline

**Implementation:**
```
ChromaFrame Core → Emscripten → WebAssembly
                               ↓
         React Component (Video Foundry Frontend)
                               ↓
              Video Foundry Backend (FastAPI)
```

---

## 3. Data Exchange Format

### 3.1 .cframe to Video Foundry Timeline

**Conversion Mapping:**

| ChromaFrame | Video Foundry |
|-------------|---------------|
| Project | Project |
| Scene | Timeline |
| Layer | Segment |
| Frame | Individual Frame |
| Raster Data | PNG/JPEG Image |
| Vector Data | SVG or Rasterized |

### 3.2 API Contract

```python
# backend/schemas/chromaframe.py
from pydantic import BaseModel

class ChromaFrameProject(BaseModel):
    name: str
    resolution: Resolution
    frame_rate: int
    scenes: List[ChromaFrameScene]

class ChromaFrameScene(BaseModel):
    name: str
    duration: int  # frames
    layers: List[ChromaFrameLayer]

class ChromaFrameLayer(BaseModel):
    name: str
    type: str  # "raster" or "vector"
    visible: bool
    opacity: float
    frames: Dict[int, ChromaFrameFrameData]

class ChromaFrameFrameData(BaseModel):
    frame_number: int
    image_data: bytes  # PNG encoded
    # or
    vector_data: Optional[str]  # SVG or custom format
```

---

## 4. Implementation Plan

### Phase 1: File Format Support (2 weeks)

**ChromaFrame Side:**
- Implement `.cframe` export with frame extraction
- Add "Export for Video Foundry" option
- Generate thumbnail previews

**Video Foundry Side:**
- Add .cframe file parser
- Extract frames to image sequence
- Create project importer API endpoint

**Deliverable:** Users can export from ChromaFrame and upload to Video Foundry

### Phase 2: API Integration (3 weeks)

**ChromaFrame Side:**
- Add Video Foundry API client
- Implement authentication (OAuth2/JWT)
- Add "Upload to Video Foundry" button

**Video Foundry Side:**
- Create ChromaFrame integration endpoints
- Add .cframe project storage
- Implement frame extraction service

**Deliverable:** Direct upload from ChromaFrame to Video Foundry

### Phase 3: Cloud Sync (4 weeks)

**ChromaFrame Side:**
- Implement cloud sync service
- Add conflict resolution
- Auto-save to cloud

**Video Foundry Side:**
- Add ChromaFrame project storage backend
- Implement real-time sync protocol (WebSockets)
- Create project versioning

**Deliverable:** Seamless cloud synchronization

### Phase 4: Enhanced Workflow (3 weeks)

**Video Foundry Side:**
- Add AI enhancement presets for 2D animation
- Implement frame interpolation
- Add style transfer specifically for cartoons

**Integration:**
- One-click AI enhancement
- Batch processing
- Preview before rendering

**Deliverable:** Complete integrated workflow

---

## 5. Technical Specifications

### 5.1 Authentication

**Method:** OAuth 2.0 with Video Foundry as provider

```cpp
// ChromaFrame: auth/VideoFoundryAuth.h
class VideoFoundryAuth {
public:
    bool login(const std::string& username, const std::string& password);
    bool refreshToken();
    std::string getAccessToken();
    bool isAuthenticated();

private:
    std::string accessToken_;
    std::string refreshToken_;
    time_t tokenExpiry_;
};
```

### 5.2 File Upload

**Method:** Multipart form upload via HTTPS

```cpp
// ChromaFrame: api/VideoFoundryClient.h
class VideoFoundryClient {
public:
    struct UploadProgress {
        size_t bytesUploaded;
        size_t totalBytes;
        float percentage;
    };

    using ProgressCallback = std::function<void(UploadProgress)>;

    bool uploadProject(
        const std::string& projectPath,
        ProgressCallback callback
    );

    std::string getProjectUrl(const std::string& projectId);
};
```

### 5.3 Cloud Sync Protocol

**Protocol:** WebSocket-based real-time sync

```json
// Sync message format
{
  "type": "project_update",
  "project_id": "uuid",
  "timestamp": "2025-01-13T12:00:00Z",
  "changes": [
    {
      "operation": "layer_add",
      "scene_index": 0,
      "layer_data": {...}
    },
    {
      "operation": "frame_update",
      "scene_index": 0,
      "layer_index": 2,
      "frame_number": 42,
      "frame_data": "base64_encoded_png"
    }
  ]
}
```

---

## 6. User Experience Flow

### 6.1 Export & Enhance Workflow

```
ChromaFrame Desktop
    ├─ Create 2D animation (storyboard, rough animation)
    ├─ Click "Export to Video Foundry"
    │   ├─ Authenticate (if not logged in)
    │   ├─ Select export settings
    │   │   ├─ Frame rate
    │   │   ├─ Resolution
    │   │   └─ Layers to export
    │   └─ Upload (with progress bar)
    │
    └─ Open in Video Foundry
        ├─ Browser launches automatically
        └─ Project loaded in timeline

Video Foundry Web App
    ├─ Review imported animation
    ├─ Select AI enhancement
    │   ├─ Upscale to 4K
    │   ├─ Add motion blur
    │   ├─ Apply style (anime, watercolor, etc.)
    │   └─ Frame interpolation (24fps → 60fps)
    │
    ├─ Preview enhanced result
    └─ Render final video
        └─ Download or share
```

### 6.2 Integrated Workflow

```
Video Foundry Web App
    ├─ Click "New 2D Animation"
    ├─ Choose:
    │   ├─ Launch ChromaFrame Desktop (if installed)
    │   └─ Use Web-based Editor (future)
    │
    └─ Create animation
        ├─ Auto-syncs to Video Foundry
        ├─ Apply AI effects in real-time
        └─ Final render
```

---

## 7. Security Considerations

### 7.1 Authentication

- OAuth 2.0 for user authentication
- JWT tokens for API access
- Token refresh mechanism
- Secure token storage (encrypted keychain)

### 7.2 File Transfer

- HTTPS for all file uploads
- File size limits (e.g., 500MB max)
- Virus scanning on upload
- Content validation

### 7.3 Data Privacy

- User projects stored securely
- End-to-end encryption option
- GDPR compliance
- User data deletion capabilities

---

## 8. Performance Optimization

### 8.1 Upload Optimization

- Chunked file upload
- Resume capability
- Compression before upload
- Delta sync (only changed data)

### 8.2 Frame Extraction

- Parallel frame rendering
- Caching rendered frames
- Progressive loading
- Thumbnail generation

### 8.3 Cloud Sync

- Efficient diff algorithm
- Batch updates
- Compression
- CDN for frame delivery

---

## 9. Testing Strategy

### 9.1 Integration Tests

```python
# tests/integration/test_chromaframe_integration.py
def test_upload_chromaframe_project():
    # Create test .cframe file
    project = create_test_project()

    # Upload to Video Foundry
    response = client.post(
        "/api/chromaframe/upload",
        files={"file": project}
    )

    assert response.status_code == 200
    project_id = response.json()["project_id"]

    # Verify project created
    project = db.query(Project).get(project_id)
    assert project.source_type == "chromaframe"
    assert len(project.segments) > 0
```

### 9.2 E2E Tests

- Upload from ChromaFrame → Verify in Video Foundry
- Edit in Video Foundry → Verify sync back to ChromaFrame
- Export enhanced video → Verify quality

---

## 10. Documentation Requirements

### 10.1 User Documentation

- "Getting Started with ChromaFrame + Video Foundry"
- "Exporting Your Animation"
- "Cloud Sync Setup Guide"
- Video tutorials

### 10.2 Developer Documentation

- API Reference
- Integration guide
- .cframe format specification
- SDK documentation

---

## 11. Rollout Plan

### Stage 1: Private Beta (Month 1-2)
- Select users test export/upload workflow
- Gather feedback
- Fix critical bugs

### Stage 2: Public Beta (Month 3-4)
- Open to all users
- Add cloud sync
- Monitor performance

### Stage 3: General Availability (Month 5)
- Full feature set
- Marketing launch
- Documentation complete

---

## 12. Success Metrics

- **Adoption:** 30% of Video Foundry users try ChromaFrame integration
- **Retention:** 50% of users who upload once, upload again
- **Performance:** <30s average upload time for typical project
- **Satisfaction:** 4.5/5 user rating
- **Conversion:** 20% of ChromaFrame users upgrade to Video Foundry Pro

---

## 13. Future Enhancements

- Real-time collaborative editing
- ChromaFrame plugins for Video Foundry AI effects
- Mobile app integration
- Template library (shared between platforms)
- Asset marketplace
- Live preview of AI effects in ChromaFrame

---

## Appendix: API Endpoints

### Video Foundry API

```
POST   /api/v1/chromaframe/upload
GET    /api/v1/chromaframe/projects
GET    /api/v1/chromaframe/projects/{id}
PUT    /api/v1/chromaframe/projects/{id}/sync
DELETE /api/v1/chromaframe/projects/{id}
GET    /api/v1/chromaframe/projects/{id}/frames
POST   /api/v1/chromaframe/projects/{id}/enhance
```

### ChromaFrame Cloud API

```
POST   /api/v1/projects/sync
GET    /api/v1/projects/{id}/changes
PUT    /api/v1/projects/{id}/push
GET    /api/v1/user/quota
```

---

**END OF DOCUMENT**

**Next Steps:**
1. Review integration strategy
2. Implement Phase 1 (file format support)
3. Create working prototype
4. User testing
5. Iterate based on feedback
