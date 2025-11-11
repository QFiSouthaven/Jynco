# Asset Package Foundry - Agent System

## Overview

The Asset Package Foundry is a multi-agent system designed to generate complete, schema-compliant asset packages from high-level creative prompts. This system was designed to solve the complex problem of generating multi-modal content (text, images, binary data) with strict inter-file dependencies and file system requirements.

---

## The Five Agents

### 1. Architect (Coordinator)
**File:** `Architect.md`

**Role:** Central orchestrator and strategic planner

**Key Responsibilities:**
- Parse user creative briefs
- Perform Google Search for visual reference data
- Create detailed Asset Manifests
- Coordinate all sub-agents
- Validate final package structure

**Think of it as:** The project manager who breaks down complex requests into actionable tasks

---

### 2. Quartermaster (File System Agent)
**File:** `Quartermaster.md`

**Role:** File system operations executor

**Key Responsibilities:**
- Create directory structures
- Generate Path Maps (single source of truth for file locations)
- Write files to disk
- Validate file system operations

**Think of it as:** The "hands" that physically create folders and files

**Critical Output:** The **Path Map** - a JSON object that every other agent uses to reference file locations

---

### 3. Librarian (Metadata & Schema Agent)
**File:** `Librarian.md`

**Role:** JSON and metadata file generator

**Key Responsibilities:**
- Generate all text-based schema files (.json, .vam, .vap, .vmi, .vaj)
- Enforce 100% schema compliance
- Embed file paths from Path Map into metadata
- Generate final package manifest (meta.json)

**Think of it as:** The data architect who ensures every file has perfect metadata

**Critical Templates:**
- .vam (Item Definition)
- .vap (Appearance Preset)
- .vmi (Morph Metadata)
- meta.json (Package Manifest)

---

### 4. Artist (Image Generation Agent)
**File:** `Artist.md`

**Role:** Visual asset generator

**Key Responsibilities:**
- Generate thumbnails and preview images
- Create complete PBR texture sets (Diffuse, Normal, Specular, Gloss)
- Follow strict naming conventions (UDIM format)
- Ensure visual consistency across asset sets

**Think of it as:** The visual designer who creates all 2D assets

**Outputs:**
- Asset thumbnails (.jpg)
- Scene previews (.jpg)
- PBR texture maps (Diffuse, Normal, Specular, Gloss)

---

### 5. Artificer (Binary Asset Agent)
**File:** `Artificer.md`

**Role:** Binary file generation via external tools

**Key Responsibilities:**
- Execute external command-line tools (Unity, Blender, etc.)
- Generate .vab (Asset Bundle) files
- Generate .vmb (Morph Binary) files
- Extract formulas data for Librarian
- Monitor and validate tool execution

**Think of it as:** The systems engineer who interfaces with specialized external tools

**Critical Note:** The Artificer doesn't create binaries itself - it's a wrapper that calls external applications

---

## System Architecture

### The Pipeline Flow

```
USER REQUEST
    ↓
[ARCHITECT]
    ├─→ Google Search (data grounding)
    ├─→ Create Asset Manifest
    └─→ Begin Orchestration
         ↓
    [QUARTERMASTER]
         ├─→ Create directory structure
         └─→ Generate PATH MAP ← (Single Source of Truth)
              ↓
         ┌────┴────┬────────┬──────────┐
         ↓         ↓        ↓          ↓
    [LIBRARIAN] [ARTIST] [ARTIFICER] [QUARTERMASTER]
         │         │        │          │
         │ .vmi    │ .jpg   │ .vmb     │ (writes all files)
         │ .vap    │ .png   │ .vab     │
         │ .vam    │ PBR    │          │
         └─────────┴────────┴──────────┘
              ↓
         [QUARTERMASTER]
              │ (writes all files to disk)
              ↓
         [LIBRARIAN]
              │ (generates final meta.json)
              ↓
         COMPLETE PACKAGE
```

---

## Path-as-Taxonomy Schema

The entire system is built around a strict directory structure where **the path itself defines the asset type and metadata**.

### Example Structure
```
[PackageName]/
├── meta.json
├── Saves/
│   └── scene/
│       ├── [SceneName].jpg
│       └── [SceneName].json
└── Custom/
    ├── Images/
    ├── [AssetCategory]/
    │   └── [SubCategory]/
    │       └── [CreatorName]/
    │           ├── [AssetName]/
    │           │   ├── [Base].jpg
    │           │   ├── [Base].vab
    │           │   ├── [Base].vaj
    │           │   └── [Base].vam
    │           ├── Textures/
    │           │   └── [TextureSetName]/
    │           │       ├── Diffuse.1001.jpg
    │           │       ├── Normal.1001.jpg
    │           │       ├── Specular.1001.jpg
    │           │       └── Gloss.1001.jpg
    │           ├── Morphs/
    │           │   └── [MorphRegion]/
    │           │       ├── [Name].vmb
    │           │       └── [Name].vmi
    │           └── Appearance/
    │               ├── Preset_[Name].jpg
    │               └── Preset_[Name].vap
```

---

## Key Design Principles

### 1. Single Source of Truth
The **Quartermaster's Path Map** is generated once and used by all agents. This prevents path desynchronization.

### 2. Separation of Concerns
- **Architect:** Thinks and plans
- **Quartermaster:** Creates and writes
- **Librarian:** Generates metadata
- **Artist:** Creates visuals
- **Artificer:** Executes external tools

### 3. Schema Strictness
The Librarian enforces **zero tolerance** for schema deviations. Every file must match the exact template.

### 4. Tool Wrapper Pattern
The Artificer doesn't generate binaries - it wraps external specialized tools (Unity, Blender, etc.)

### 5. Atomic File Bundles
All files for a single asset share the same base filename and directory:
- `Bangs A Alt.jpg`
- `Bangs A Alt.vab`
- `Bangs A Alt.vaj`
- `Bangs A Alt.vam`

---

## Communication Protocol

### Agent-to-Agent Messages

All agents communicate via structured JSON commands:

```json
{
  "command": "GENERATE_VMI",
  "dataPayload": {
    "morphName": "CyberRonin_Head",
    "region": "head"
  },
  "pathMap": {
    "vmb_path": "Custom/Atom/Person/Morphs/female/CyberRonin_Head.vmb"
  }
}
```

### Status Responses

All agents return standardized responses:

```json
{
  "status": "SUCCESS",
  "outputPath": "...",
  "additionalData": { ... }
}
```

or

```json
{
  "status": "FAILED",
  "error": "Description of failure",
  "details": { ... }
}
```

---

## Example: Complete Execution Flow

### User Request
> "Generate a new 'Person' asset named 'Cyber-Ronin' by creator 'Me'. I want him to have a futuristic metal-weave jacket and glowing red eyes."

### Step 1: Architect Analysis
- Parses request
- Googles "futuristic metal-weave jacket" and "cyberpunk glowing eyes"
- Creates Asset Manifest:
  - Person asset
  - Appearance preset (.vap)
  - Head morph (.vmb + .vmi)
  - Body morph (.vmb + .vmi)
  - Jacket textures (PBR set)

### Step 2: Quartermaster - Structure Creation
Creates directories:
```
Custom/Atom/Person/Appearance/
Custom/Atom/Person/Morphs/female/
Custom/Atom/Person/Textures/Me/Jacket/
```

Generates Path Map:
```json
{
  "appearance_preset": "Custom/Atom/Person/Appearance/Preset_CyberRonin.vap",
  "appearance_thumb": "Custom/Atom/Person/Appearance/Preset_CyberRonin.jpg",
  "morph_head_vmb": "Custom/Atom/Person/Morphs/female/CyberRonin_Head.vmb",
  "morph_head_vmi": "Custom/Atom/Person/Morphs/female/CyberRonin_Head.vmi",
  "texture_diffuse": "Custom/Atom/Person/Textures/Me/Jacket/Diffuse.1001.jpg"
}
```

### Step 3: Parallel Agent Execution

**Artist:**
- Generates thumbnail for preset
- Generates PBR texture set for jacket (using Google reference data)

**Artificer:**
- Calls external tool to generate head morph binary
- Calls external tool to generate body morph binary
- Returns formulas data to Architect

**Librarian:**
- Receives Path Map
- Receives formulas from Artificer
- Generates .vmi files with correct paths and formulas
- Generates .vap file with correct texture paths

### Step 4: Quartermaster - File Writing
Receives all generated content and writes:
- All metadata files (.vmi, .vap)
- All image files (.jpg for thumb and textures)
- Binary files already written by Artificer

### Step 5: Librarian - Final Manifest
Generates meta.json with complete file list

### Step 6: Complete
Package delivered to user

---

## Implementation Notes

### Current Status
These agent definitions are **system prompts** - detailed specifications for how each agent should behave.

### Next Steps for Implementation
1. **Backend API**: Build a service that implements these agents
2. **Tool Integration**: Connect external tools for Artificer
3. **Image Generation**: Connect to image generation APIs for Artist
4. **File System**: Implement actual file operations for Quartermaster

### Wizard of Oz MVP
For initial validation without full implementation:
- **Architect**: AI model (Gemini/Claude) with this system prompt
- **Quartermaster**: Manual file creation by human operator
- **Librarian**: AI model generating JSON, human copies to files
- **Artist**: Human uses image generator with AI-provided prompts
- **Artificer**: Human creates placeholder binary files

This proves the business model before investing in full automation.

---

## Why This Architecture?

### Problem It Solves
Creating asset packages requires:
1. **Multi-modal generation**: Text (JSON), images (textures), binaries (.vmb, .vab)
2. **Strict dependencies**: File A must reference the exact path of File B
3. **Schema compliance**: JSON must match exact templates
4. **File system operations**: Directories and files must be created in specific structure

**A single monolithic AI model cannot handle all of this.**

### Solution
Break the problem into specialized agents:
- Each handles one concern
- All coordinate through the Architect
- Path Map ensures synchronization
- Templates ensure compliance

---

## File Type Reference

### Text-Based Files (Librarian)
- **.vam** - Item definition (JSON)
- **.vap** - Appearance preset (JSON)
- **.vmi** - Morph metadata (JSON)
- **.vaj** - Asset bundle metadata (JSON)
- **meta.json** - Package manifest

### Image Files (Artist)
- **.jpg** - Thumbnails and diffuse textures
- **.png** - High-quality normal/specular maps

### Binary Files (Artificer)
- **.vmb** - Morph binary (vertex deltas)
- **.vab** - Asset bundle (Unity bundle)

---

## Success Criteria

A successfully generated package must:
1. ✓ Follow exact Path-as-Taxonomy structure
2. ✓ Have all files with correct naming (atomicity)
3. ✓ Have all metadata files with valid JSON schemas
4. ✓ Have all file path references correct (no broken links)
5. ✓ Include complete meta.json with all files listed
6. ✓ Have PBR textures following UDIM convention
7. ✓ Have morph .vmi/.vmb pairs with matching data

---

## For Developers

When implementing these agents:

1. **Read all 5 agent documents** - Each contains specific templates and requirements
2. **Start with Quartermaster** - It provides the foundation (Path Map)
3. **Implement Librarian next** - It validates the schema system works
4. **Add Artist** - Proves multi-modal generation
5. **Add Artificer last** - Most complex (external tool integration)
6. **Build Architect** - Once all workers are functional

---

## For Business/Product

This system enables:
- **Automated asset package generation** from natural language
- **SaaS business model** - charge per package generated
- **Quality guarantee** - 100% schema compliance
- **Scalability** - agents can run in parallel
- **Flexibility** - swap out image generators, external tools, etc.
