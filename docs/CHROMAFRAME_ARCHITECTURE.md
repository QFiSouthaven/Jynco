# ChromaFrame - 2D Animator Architecture Proposal

**Version:** 1.0
**Date:** January 2025
**Status:** Design Phase

---

## Executive Summary

ChromaFrame is a sophisticated 2D flip-book style animation application with industry-standard tools and video rendering capabilities. This document outlines the high-level architectural design, implementation roadmap, and integration strategy with the Video Foundry platform.

**Key Objectives:**
- Professional-grade 2D animation toolset
- Real-time drawing performance
- Hybrid raster/vector workflow
- Industry-standard video export
- Seamless Video Foundry integration

---

## 1. Guiding Principles

This architecture is designed based on the following core principles, directly addressing potential risks:

### 1.1 Modularity & Decoupling
Components will be designed as independent modules with well-defined interfaces. This mitigates scope creep by allowing features to be developed, replaced, or enhanced in isolation.

### 1.2 Performance First
The core graphics and data handling systems must be optimized for real-time feedback during drawing and playback, preventing performance bottlenecks.

### 1.3 Extensibility
The architecture must easily accommodate new tools, layer types, and export formats without requiring a full system rewrite.

### 1.4 Platform Agnostic Core
The core logic, data model, and rendering engine will be designed to be independent of the underlying operating system and UI framework, ensuring future portability.

---

## 2. Core Architecture Overview

We adopt a **Modular, Service-Oriented Architecture**. This breaks the application into distinct, logical services that communicate through a central `Application Core`.

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Viewport   │  │   Timeline   │  │ Tool Palette │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                  │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │ User Actions
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Core                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Project Manager  │  Tool Service  │  Timeline Service   │  │
│  │  Command Manager  │  Playback      │  History Manager    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Core Engine & Services                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Graphics & Canvas Engine  (OpenGL/Vulkan)               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Animation Data Model      (Hierarchical Structure)      │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Rendering & Export Pipeline  (FFmpeg Integration)       │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ File I/O & Persistence   (.cframe Format)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Libraries                            │
│   OpenGL/Vulkan  │  FFmpeg  │  Qt 6  │  Custom Formats         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2.1. Component Breakdown

### UI Layer
The user-facing component responsible for:
- Rendering UI elements (canvas, timeline, palettes)
- Capturing user input (mouse, stylus, keyboard)
- Translating user actions into commands
- Reflecting Animation Data Model state

**Technology:** Qt 6 Widgets/QML

### Application Core

**Project Manager:**
- Handles project-level operations (new, open, save, close)
- Manages project metadata
- Coordinates file I/O operations

**Tool Service:**
- Manages currently active tool state
- Applies tool logic to data model
- Provides tool-specific settings

**Timeline & Playback Service:**
- Controls animation playback
- Manages current frame navigation
- Handles onion skinning
- Synchronizes playback with audio (future)

**Command & History Manager:**
- Implements command pattern for all state changes
- Provides robust Undo/Redo functionality
- Manages command queue
- Supports macro commands (grouped operations)

### Core Engine & Services

**Graphics & Canvas Engine:**
- High-performance drawing operations
- Direct GPU acceleration via OpenGL
- Renders canvas, brushes, onion skins, UI overlays
- Low-latency real-time feedback
- Optimized for stylus input

**Animation Data Model:**
- Single source of truth for project state
- Hierarchical data structure (Project → Scene → Layer → Frame)
- Pure data representation (display-agnostic)
- Observable for UI synchronization
- Memory-efficient sparse storage

**Rendering & Export Pipeline:**
- Asynchronous multi-threaded rendering
- Frame-by-frame composition
- FFmpeg integration for video encoding
- Progress tracking and cancellation
- Multiple export formats

**File I/O & Persistence Service:**
- Custom `.cframe` file format
- Efficient serialization/deserialization
- Incremental save support
- Auto-save functionality
- Project backup management

---

## 3. Technology Stack

### 3.1 Core Technologies

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| **Language** | C++ | C++17/20 | Low-level control, high performance, GPU access, mature ecosystem |
| **UI Framework** | Qt | 6.5+ | Cross-platform, OpenGL integration, rich widgets, industry-proven |
| **Graphics API** | OpenGL | 3.3+ Core | Performance, compatibility, accessibility, migration path to Vulkan |
| **Video Encoding** | FFmpeg | 5.0+ | Industry standard, format support, codec flexibility |
| **Build System** | CMake | 3.20+ | Cross-platform, modern, Qt integration |
| **Testing** | Google Test | Latest | C++ standard, well-documented |

### 3.2 File Format

**Custom `.cframe` Format:**
- ZIP archive container
- `project.json` - Manifest and metadata
- `data/` - Binary frame/layer data
- `assets/` - Referenced images, audio (future)
- `thumbnails/` - Preview images
- Extensible and version-safe

**Benefits:**
- Human-readable metadata (JSON)
- Efficient binary storage for pixel data
- Easy to inspect and debug
- Forward/backward compatibility
- Standard compression

---

## 4. Data Model Design

### 4.1 Hierarchical Structure

```cpp
Project
├── Metadata (resolution, framerate, colorspace)
├── GlobalPalette
└── Scenes[]
    └── Scene
        ├── Duration
        └── Layers[]
            └── Layer (Abstract)
                ├── RasterLayer
                │   └── Frames[]
                │       └── RasterFrame
                │           └── PixelData (bitmap)
                │
                └── VectorLayer
                    └── Frames[]
                        └── VectorFrame
                            └── Strokes[]
                                └── Stroke
                                    ├── Points[]
                                    ├── Pressure[]
                                    ├── BrushSettings
                                    └── Color
```

### 4.2 Core Data Classes

```cpp
// Project.h
class Project {
public:
    std::string name;
    Resolution resolution;
    int frameRate;
    ColorSpace colorSpace;
    std::vector<Scene> scenes;
    GlobalPalette palette;

    void save(const std::string& path);
    static Project load(const std::string& path);
};

// Scene.h
class Scene {
public:
    std::string name;
    int duration;  // frames
    std::vector<std::unique_ptr<Layer>> layers;

    void addLayer(std::unique_ptr<Layer> layer);
    void removeLayer(int index);
    void reorderLayer(int from, int to);
};

// Layer.h (Abstract Base)
class Layer {
public:
    virtual ~Layer() = default;

    std::string name;
    bool visible = true;
    float opacity = 1.0f;
    BlendMode blendMode;

    virtual void render(Frame frame, RenderContext& ctx) = 0;
    virtual FrameData* getFrame(int frameNumber) = 0;
};

// RasterLayer.h
class RasterLayer : public Layer {
public:
    void render(Frame frame, RenderContext& ctx) override;
    RasterFrame* getFrame(int frameNumber) override;

private:
    std::map<int, std::unique_ptr<RasterFrame>> frames_;
};

// VectorLayer.h
class VectorLayer : public Layer {
public:
    void render(Frame frame, RenderContext& ctx) override;
    VectorFrame* getFrame(int frameNumber) override;

private:
    std::map<int, std::unique_ptr<VectorFrame>> frames_;
};

// Stroke.h
class Stroke {
public:
    std::vector<Point2D> points;
    std::vector<float> pressures;
    std::vector<float> tilts;
    BrushSettings brush;
    Color color;

    void addPoint(Point2D point, float pressure, float tilt);
    void smooth(int iterations);
};
```

### 4.3 Sparse Frame Storage

Frames are stored sparsely - only keyframes contain actual data. In-between frames reference the previous keyframe.

**Benefits:**
- Minimal memory footprint
- Fast frame navigation
- Easy keyframe management
- Efficient for tweening (future)

---

## 5. Key System Flows

### 5.1 User Draws a Stroke on Canvas

```
┌─────────────┐
│  UI Layer   │
│ (Mouse/     │
│  Stylus)    │
└──────┬──────┘
       │ 1. Capture Input Events
       │    (position, pressure, tilt)
       ▼
┌─────────────────────┐
│  Tool Service       │
│  (DrawStroke        │
│   Command)          │
└──────┬──────────────┘
       │ 2. Create Command
       ▼
┌─────────────────────┐
│  Command Manager    │
│  (Execute & Store)  │
└──────┬──────────────┘
       │ 3. Update Model
       ▼
┌─────────────────────┐
│  Animation Data     │
│  Model              │
│  (Add Stroke)       │
└──────┬──────────────┘
       │ 4. Emit ModelChanged Signal
       ▼
┌─────────────────────┐
│  Graphics Engine    │
│  (Re-render via     │
│   OpenGL)           │
└──────┬──────────────┘
       │ 5. Update Display
       ▼
┌─────────────┐
│  UI Layer   │
│  (Canvas    │
│   Updated)  │
└─────────────┘
```

**Performance Optimization:**
- Stroke points batched during drawing
- Partial canvas updates (dirty regions)
- GPU-accelerated rendering
- Double-buffered display

### 5.2 User Renders Video File

```
┌─────────────┐
│  UI Layer   │
│ (Render     │
│  Button)    │
└──────┬──────┘
       │ 1. Initiate Render
       ▼
┌─────────────────────┐
│  Application Core   │
│  (Validate Settings)│
└──────┬──────────────┘
       │ 2. Start Pipeline
       ▼
┌─────────────────────────────────┐
│  Rendering Pipeline             │
│  (Background Thread)            │
│                                 │
│  For each frame 1..N:           │
│  ┌─────────────────────────┐   │
│  │ 1. Graphics Engine      │   │
│  │    Render to Offscreen  │   │
│  │    Buffer               │   │
│  ├─────────────────────────┤   │
│  │ 2. Read Pixel Data      │   │
│  ├─────────────────────────┤   │
│  │ 3. Send to FFmpeg       │   │
│  │    Encoder              │   │
│  └─────────────────────────┘   │
│                                 │
└──────┬──────────────────────────┘
       │ 3. Progress Updates
       ▼
┌─────────────┐
│  UI Layer   │
│ (Progress   │
│  Bar)       │
└──────┬──────┘
       │ 4. Completion
       ▼
┌─────────────┐
│  File       │
│  Saved!     │
└─────────────┘
```

**Implementation Details:**
- Multi-threaded rendering (thread pool)
- Frame queue for smooth encoding
- Memory-mapped I/O for large frames
- Cancellable operation
- Error recovery

---

## 6. Risk Mitigation

### 6.1 Scope Creep

**Risk:** Feature requests expanding beyond initial scope

**Mitigation:**
- Modular architecture allows incremental development
- MVP approach: Launch with core raster tools
- Add vector layers, advanced brushes as separate modules
- Clear feature roadmap with phases

### 6.2 Performance Bottlenecks

**Risk:** Slow drawing or playback

**Mitigation:**
- **Drawing Performance:**
  - C++ with direct OpenGL rendering
  - GPU-accelerated brush rendering
  - Optimized data structures
  - Dirty region tracking
  - Stroke simplification

- **Rendering Performance:**
  - Background thread for export
  - Frame caching
  - Parallel rendering (multiple frames)
  - Progressive encoding

### 6.3 Complexity & Platform Support

**Risk:** Difficult to maintain across platforms

**Mitigation:**
- Qt abstracts platform differences
- OpenGL provides cross-platform graphics
- Automated testing on all platforms
- CI/CD for multi-platform builds
- Clear platform abstraction layers

### 6.4 FFmpeg Integration Complexity

**Risk:** Difficult to integrate and configure

**Mitigation:**
- Use FFmpeg as library, not CLI
- Wrapper class for simplified API
- Pre-built FFmpeg binaries for each platform
- Comprehensive error handling
- Format presets for common use cases

---

## 7. Video Foundry Integration

### 7.1 Integration Architecture

ChromaFrame can integrate with Video Foundry in multiple ways:

**Option 1: Standalone Desktop App with Export**
```
ChromaFrame (Desktop)
    ├─ Edit Animation
    ├─ Export .cframe project
    └─ Upload to Video Foundry
         └─ Video Foundry processes as AI input
```

**Option 2: Video Foundry Plugin/Service**
```
Video Foundry Platform
    ├─ Web Frontend (React)
    ├─ Backend API (FastAPI)
    └─ ChromaFrame Service (C++ microservice)
         ├─ Render API endpoint
         └─ Generate animation frames
```

**Option 3: Hybrid Approach**
```
ChromaFrame Desktop App
    ├─ Local editing
    ├─ Cloud sync to Video Foundry
    └─ Collaborative features

Video Foundry Cloud
    ├─ Store .cframe projects
    ├─ Render in cloud
    └─ AI enhancement
```

### 7.2 Integration Points

1. **File Format Compatibility**
   - Export .cframe to image sequence
   - Video Foundry imports as ComfyUI input
   - Timeline segment integration

2. **API Integration**
   - ChromaFrame REST API for rendering
   - Video Foundry calls ChromaFrame service
   - Authentication via Video Foundry tokens

3. **Workflow Integration**
   - Create animation in ChromaFrame
   - Export to Video Foundry timeline
   - Apply AI effects
   - Final composition

---

## 8. Development Phases

### Phase 1: Core Foundation (8 weeks)
- Project structure and build system
- Basic Qt UI skeleton
- Animation data model
- OpenGL canvas with simple brush
- Basic file I/O (.cframe format)

**Deliverable:** Working prototype with single-layer raster drawing

### Phase 2: Drawing Tools (6 weeks)
- Brush engine (pressure, tilt support)
- Eraser tool
- Color picker and palette
- Undo/Redo system
- Layer management UI

**Deliverable:** Functional drawing application

### Phase 3: Timeline & Playback (4 weeks)
- Timeline UI component
- Frame navigation
- Onion skinning
- Playback engine
- Frame rate control

**Deliverable:** Flip-book animation capability

### Phase 4: Export Pipeline (6 weeks)
- FFmpeg integration
- Rendering pipeline
- Export settings UI
- Progress tracking
- Format presets (MP4, MOV, GIF)

**Deliverable:** Video export functionality

### Phase 5: Vector Support (8 weeks)
- Vector layer implementation
- Vector stroke engine
- Path editing tools
- Vector-to-raster conversion

**Deliverable:** Hybrid raster/vector workflow

### Phase 6: Polish & Integration (4 weeks)
- Performance optimization
- Video Foundry integration
- User testing
- Bug fixes
- Documentation

**Deliverable:** Production-ready release

**Total:** 36 weeks (~9 months)

---

## 9. Success Metrics

- **Performance:** <16ms frame render time (60 FPS)
- **Responsiveness:** <50ms stylus input latency
- **Stability:** <1 crash per 1000 user hours
- **Export Speed:** >30 FPS encoding speed
- **Memory:** <2GB RAM for typical project
- **File Size:** <10MB per minute of animation

---

## 10. Future Enhancements

- Audio track support
- Advanced brushes (watercolor, oil paint simulation)
- 3D camera movements
- Particle effects
- Tweening and interpolation
- Collaborative editing
- Plugin system
- Mobile companion app
- Cloud rendering

---

## Appendix A: Technology Alternatives Considered

### UI Framework
- **Rejected: Electron** - Performance concerns for graphics-intensive app
- **Rejected: ImGui** - Not designed for complex application UI
- **Selected: Qt 6** - Best balance of features, performance, cross-platform

### Graphics API
- **Rejected: DirectX** - Windows-only
- **Rejected: Metal** - macOS-only
- **Considered: Vulkan** - More complex, better for future migration
- **Selected: OpenGL** - Proven, accessible, sufficient performance

### Language
- **Rejected: Rust** - Steeper learning curve, smaller ecosystem
- **Rejected: C#** - Performance and cross-platform concerns
- **Selected: C++** - Industry standard for graphics applications

---

**END OF DOCUMENT**

**Next Steps:**
1. Review and approval
2. Detailed technical specifications
3. Prototype development
4. User testing
5. Iteration
