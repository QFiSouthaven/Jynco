# ChromaFrame - 2D Flip-Book Animator

**Status:** Design Phase
**Version:** 0.1.0 (Planned)
**Platform:** Cross-platform (Windows, macOS, Linux)

---

## Overview

ChromaFrame is a professional-grade 2D flip-book style animation application with industry-standard drawing tools and seamless Video Foundry integration. Built with C++, Qt 6, and OpenGL for maximum performance and cross-platform compatibility.

---

## Features (Planned)

### Core Animation
- ✨ **Frame-by-frame animation** with onion skinning
- 🎨 **Professional drawing tools** with pressure sensitivity
- 📊 **Timeline editor** with layer management
- 🔄 **Hybrid raster/vector workflow**
- 💾 **Custom .cframe file format**

### Performance
- ⚡ **Real-time rendering** with OpenGL acceleration
- 🎯 **<16ms frame time** (60 FPS)
- 📝 **Low-latency stylus input** (<50ms)
- 🧠 **Efficient memory usage** (<2GB for typical projects)

### Export & Integration
- 🎬 **Industry-standard video export** via FFmpeg
- 🔗 **Video Foundry integration** for AI enhancement
- 📤 **Cloud sync** for collaboration
- 🌐 **Multiple export formats** (MP4, MOV, GIF, Image Sequence)

---

## Architecture

ChromaFrame uses a modular, service-oriented architecture:

```
UI Layer (Qt 6)
    ↓
Application Core
    ├─ Project Manager
    ├─ Tool Service
    ├─ Timeline Service
    └─ Command Manager (Undo/Redo)
    ↓
Core Engine
    ├─ Graphics Engine (OpenGL)
    ├─ Animation Data Model
    ├─ Rendering Pipeline (FFmpeg)
    └─ File I/O (.cframe format)
```

See [Architecture Document](../docs/CHROMAFRAME_ARCHITECTURE.md) for complete details.

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | C++ | C++17/20 |
| UI Framework | Qt | 6.5+ |
| Graphics | OpenGL | 3.3+ Core |
| Video | FFmpeg | 5.0+ |
| Build System | CMake | 3.20+ |
| Testing | Google Test | Latest |

---

## Project Structure

```
chromaframe/
├── src/                  # Source code
│   ├── core/            # Core engine
│   ├── ui/              # Qt UI components
│   ├── graphics/        # OpenGL rendering
│   ├── tools/           # Drawing tools
│   └── export/          # FFmpeg export pipeline
├── include/             # Public headers
├── tests/               # Unit tests
├── docs/                # Documentation
├── assets/              # Icons, resources
├── CMakeLists.txt       # Build configuration
└── README.md            # This file
```

---

## Building (Planned)

### Prerequisites

- C++17 compatible compiler (GCC 9+, Clang 10+, MSVC 2019+)
- CMake 3.20+
- Qt 6.5+
- FFmpeg development libraries

### Build Instructions

**Linux/Mac:**
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
./chromaframe
```

**Windows:**
```powershell
mkdir build && cd build
cmake -G "Visual Studio 16 2019" ..
cmake --build . --config Release
.\Release\chromaframe.exe
```

---

## Video Foundry Integration

ChromaFrame integrates seamlessly with Video Foundry for AI-enhanced video generation:

### Export to Video Foundry
1. Create your 2D animation in ChromaFrame
2. Click "Export to Video Foundry"
3. Authenticate with your Video Foundry account
4. Project automatically uploaded and converted
5. Apply AI effects in Video Foundry web interface

### Cloud Sync
- Sign in with Video Foundry account
- Projects automatically sync to cloud
- Access from any device
- Collaborative editing (future)

See [Integration Strategy](../docs/CHROMAFRAME_INTEGRATION_STRATEGY.md) for details.

---

## Development Roadmap

### Phase 1: Core Foundation (8 weeks)
- [ ] Project structure and build system
- [ ] Basic Qt UI skeleton
- [ ] Animation data model
- [ ] OpenGL canvas with simple brush
- [ ] Basic file I/O (.cframe format)

### Phase 2: Drawing Tools (6 weeks)
- [ ] Brush engine (pressure, tilt)
- [ ] Eraser tool
- [ ] Color picker and palette
- [ ] Undo/Redo system
- [ ] Layer management UI

### Phase 3: Timeline & Playback (4 weeks)
- [ ] Timeline UI component
- [ ] Frame navigation
- [ ] Onion skinning
- [ ] Playback engine

### Phase 4: Export Pipeline (6 weeks)
- [ ] FFmpeg integration
- [ ] Rendering pipeline
- [ ] Export settings UI
- [ ] Progress tracking

### Phase 5: Vector Support (8 weeks)
- [ ] Vector layer implementation
- [ ] Vector stroke engine
- [ ] Path editing tools

### Phase 6: Polish & Integration (4 weeks)
- [ ] Performance optimization
- [ ] Video Foundry integration
- [ ] User testing
- [ ] Documentation

**Total:** ~9 months

---

## Documentation

- [Architecture Design](../docs/CHROMAFRAME_ARCHITECTURE.md) - Complete architectural specification
- [Integration Strategy](../docs/CHROMAFRAME_INTEGRATION_STRATEGY.md) - Video Foundry integration plan
- [Technical Specifications](../docs/CHROMAFRAME_TECHNICAL_SPEC.md) - Detailed technical docs (coming soon)
- [User Guide](docs/USER_GUIDE.md) - End-user documentation (coming soon)
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Contributing guide (coming soon)

---

## Contributing

ChromaFrame is part of the Video Foundry project. We welcome contributions!

### Getting Started
1. Read the [Architecture Document](../docs/CHROMAFRAME_ARCHITECTURE.md)
2. Check the [Contributing Guide](../CONTRIBUTING.md)
3. Set up your development environment
4. Pick an issue or feature from the roadmap
5. Submit a pull request

### Development Setup
(Coming soon - Phase 1)

---

## License

MIT License - see [LICENSE](../LICENSE) file for details.

---

## Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/QFiSouthaven/Jynco/issues)
- **Discussions**: [GitHub Discussions](https://github.com/QFiSouthaven/Jynco/discussions)

---

## Acknowledgments

ChromaFrame is inspired by professional animation tools like:
- Adobe Animate
- Toon Boom Harmony
- Krita
- OpenToonz

Built with:
- [Qt Framework](https://www.qt.io/)
- [OpenGL](https://www.opengl.org/)
- [FFmpeg](https://ffmpeg.org/)

---

## Status

**Current Phase:** Design & Planning

ChromaFrame is currently in the design phase. The architecture and integration strategy have been finalized. Implementation will begin in Q1 2025.

**Want to help?** Check out the [Contributing Guide](../CONTRIBUTING.md) or join the discussion!

---

**Part of the [Video Foundry](../README.md) Platform** 🎬
