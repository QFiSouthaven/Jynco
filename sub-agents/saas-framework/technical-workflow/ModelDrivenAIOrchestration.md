# Technical Workflow: Model-Driven AI Orchestration (MDAO)

Based on your directives, I am proceeding as an ideal analytical partner.

---

## 1. Deconstruction and Assumption Validation

Your high-level goal is to create a SaaS. Your methodology is to act as a "non-coder AI enthusiast," orchestrating a specific set of tools:
- **Google AI Studio** (for building/prototyping)
- **Claude Code** (for code generation)
- **Draw.io** (for architecture)
- **"Small nifty prompts"** (as the control logic)

Your strategy is to automate the build process by first creating small, internal tools.

### Core Assumptions

I am proceeding on two assumptions:

1. You have a specific SaaS concept (the "bigger picture") in mind, and your request is about *optimizing the workflow* to build it.

2. The phrase "Grab data some how" represents the core data model of your application, which is currently the most critical undefined variable.

---

## 2. Proactive Flaw Analysis

Your workflow is logical, but it contains two critical flaws that will guarantee failure if not neutralized.

### Flaw 1 (Critical): The Data Model Fallacy

**Problem:** You've listed "Grab data some how" as a late-stage step. In any SaaS application, the data model is not *a* step; it is *the first* step and the absolute foundation.

**Impact:** If you use Claude to build "small tools" before a *strict, machine-readable data schema* is defined, 100% of that generated code will be based on incorrect assumptions. You will be forced to refactor your entire codebase the moment your data needs are finalized, negating all your automation efforts.

---

### Flaw 2 (High): The Tool Disconnection Fallacy

**Problem:** Your tools (AI Studio, Claude, Draw.io) are disconnected. Your current workflow implies a manual process:
1. Look at Draw.io diagram
2. Manually write a "nifty prompt"
3. Paste into Claude
4. Copy code from Claude
5. Paste into AI Studio

**Impact:** This manual copy-paste process is slow, error-prone, and unscalable. It makes *you* the bottleneck. If you change the architecture in Draw.io, you have no way to automatically update your prompts or code, leading to a complete desynchronization of your project.

---

## 3. Non-Obvious Solution: Model-Driven AI Orchestration (MDAO)

To neutralize these flaws, you must "build small tools first." But the *first* tool you build must not be a SaaS feature. It must be the *automation pipeline itself*.

### The Paradigm Shift

The non-obvious paradigm shift (your "Cross-Domain Leap") is to stop treating Draw.io as a *drawing* tool and start treating it as a **Model-Based Systems Engineering (MBSE)** tool. The diagram must become the *single source of truth*—a machine-readable "master prompt" that *drives* both Claude and AI Studio.

---

## The 4-Step MDAO Workflow

### Step 1: Define the Data Contract

**Neutralizes Flaw 1: The Data Model Fallacy**

Before you draw a single box, you will use AI Studio to define your data model.

**Action:** Do not ask for code. Ask for a *schema*.

**Non-Coder Tip:** The "small nifty prompt" to use is:
```
I am building a SaaS. Generate a complete `JSON Schema` for my database.
I need tables for `Users`, `Projects`, and `Tasks`.
```

**Result:** You will get a file (e.g., `schema.json`). This file is now your **Data Contract**. It is the non-negotiable source of truth that you will provide to Claude for *every subsequent prompt*.

**Why This Works:**
- Establishes data structure before any code
- Prevents schema drift and refactoring
- Provides consistent contract for all AI code generation
- Machine-readable and version-controllable

---

### Step 2: Make the Diagram the Master Prompt

**Neutralizes Flaw 2: The Tool Disconnection Fallacy**

This is the core of the MDAO framework. You will embed your "nifty prompts" *inside* your Draw.io diagram.

**Action:**

1. Open Draw.io and create your user flow diagram (e.g., a box for "User Login Screen," a box for "Project Dashboard").

2. Right-click the "User Login Screen" box.

3. Select **"Edit Data"** (or `Ctrl+M`).

4. Add a new property with the following key-value pair:
   - **Key:** `claude_prompt`
   - **Value:**
   ```
   Using the attached 'schema.json' as a data contract, generate a Python FastAPI
   endpoint for user login. The endpoint must validate input against the 'Users'
   schema. Also, generate the HTML and vanilla JavaScript frontend for this login form.
   ```

**Result:** Your Draw.io file (which is just XML) now *contains* your entire prompt library, perfectly synchronized with your architecture.

**Key Benefits:**
- Single source of truth for both architecture AND prompts
- Visual representation linked directly to generation instructions
- Changes to diagram automatically reflect in prompts
- No manual synchronization needed

---

### Step 3: Build Your First Automation Tool (The "Parser")

This is your *first* "small tool." It will read your diagram and extract your prompts for you.

**Action:** Use Google AI Studio or Claude to build this tool.

**Prompt:**
```
Write a Python script that can read a `.drawio` file, parse its XML, find all
shapes that have a metadata property named `claude_prompt`, and print the value
of that property to the console.
```

**Result:** You now have a script (e.g., `run_build.py`). When you run it, it automatically reads your architecture and outputs a list of all the generation tasks you need Claude to perform.

**Script Capabilities:**
- Parse Draw.io XML format
- Extract custom metadata from shapes
- Output structured list of prompts
- Can be extended to automatically call Claude API

---

### Step 4: Execute the Automated Workflow

Your new, automated workflow is as follows:

#### 1. DESIGN
You update your SaaS architecture in **Draw.io**, adding or editing the `claude_prompt` metadata in each shape.

#### 2. EXTRACT
You run your Python tool (`python run_build.py`) to extract all prompts from your diagram.

#### 3. GENERATE
You pipe this list of prompts (along with your `schema.json` contract) into **Claude Code** to generate all the required code snippets (API endpoints, frontend components).

#### 4. BUILD
You use **Google AI Studio** to *assemble* these generated, schema-compliant code snippets into a runnable prototype.

---

## The Transformation

This MDAO framework turns you from a "copy-paster" into an *orchestrator*. Your single point of work is the Draw.io diagram, and your "small tools" (the parser, the prompts) execute your architectural vision automatically.

---

## Key Advantages of MDAO

### 1. Single Source of Truth
- Draw.io diagram contains both visual architecture AND generation logic
- No desynchronization between design and implementation

### 2. Automation Over Manual Work
- Eliminate copy-paste workflow
- Reduce human error
- Scale to large projects

### 3. Data-First Approach
- Schema defined before code
- Consistent data contracts across all components
- Prevents costly refactoring

### 4. Tool Orchestration
- Each tool plays to its strengths
- Draw.io: Architecture visualization + prompt storage
- Claude: Code generation
- AI Studio: Prototyping and assembly
- Parser: Automation glue

### 5. Non-Coder Friendly
- No direct coding required
- Visual diagram-driven development
- AI tools handle code generation
- Focus on architecture and logic, not syntax

---

## Implementation Checklist

- [ ] Define JSON Schema for your data model (`schema.json`)
- [ ] Create Draw.io architecture diagram
- [ ] Add `claude_prompt` metadata to each shape/component
- [ ] Build parser tool to extract prompts from Draw.io XML
- [ ] Test extraction workflow
- [ ] Set up Claude Code with schema contract
- [ ] Generate code components
- [ ] Assemble in Google AI Studio
- [ ] Iterate: Update diagram → Extract → Generate → Build

---

## Extended Capabilities

Once the basic MDAO pipeline is established, you can extend it:

### Advanced Features
- **Version Control:** Track Draw.io diagram changes in Git
- **API Integration:** Have parser automatically call Claude API
- **Testing:** Generate test cases from diagram metadata
- **Documentation:** Auto-generate docs from architecture
- **Deployment:** Add deployment instructions to diagram metadata

### Metadata Extensions
Beyond `claude_prompt`, you can add:
- `test_requirements`: Testing criteria
- `api_endpoint`: Endpoint specifications
- `dependencies`: Required libraries
- `deployment_config`: Deployment parameters

---

## Summary

The Model-Driven AI Orchestration (MDAO) framework transforms disconnected tools into an integrated, automated development pipeline. By treating Draw.io as a machine-readable source of truth and embedding generation logic directly in architectural diagrams, non-coders can orchestrate complex SaaS development without manual copy-paste workflows.

**Core Principle:** Your architecture diagram IS your codebase specification. Everything else is automated extraction and generation.
