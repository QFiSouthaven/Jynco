# Jynco Examples

This directory contains example scripts demonstrating various Jynco workflows and features.

## Available Examples

### 1. Parallel Initialization Demo (`parallel_initialization_demo.py`)

**The main showcase demonstrating all agents working in parallel.**

Features:
- Initializes all 5 agents concurrently
- Creates infrastructure (cache + job queue)
- Demonstrates parallel operations across agents
- Shows agent status monitoring
- Creates a complete demo project

Run:
```bash
python examples/parallel_initialization_demo.py
```

Expected output:
```
🏗️  Initializing infrastructure...
✓ Cache initialized: local
✓ Job queue initialized: memory

🤖 Initializing agents...
✓ Storyboard Agent initialized
✓ Motion Agent initialized
✓ Render Agent initialized
✓ Quartermaster Agent initialized
✓ Architect Agent initialized
✓ All agent dependencies wired

[... full agent status report ...]

✅ Demo completed successfully!
```

### 2. Simple Workflow (`simple_workflow.py`)

**A minimal example for getting started quickly.**

Features:
- Basic project creation
- Storyboard initialization
- Adding clips to timeline
- Reading storyboard state

Run:
```bash
python examples/simple_workflow.py
```

## What Gets Created

When you run these examples, the following directory structure is created:

```
./
├── projects/
│   └── proj_*/
│       ├── clips/
│       ├── assets/
│       │   ├── images/
│       │   └── audio/
│       ├── exports/
│       └── storyboard.json
├── cache/
│   ├── metadata/
│   └── files/
└── temp/
```

## Understanding the Output

### Parallel Demo Timeline

1. **Infrastructure Init** - Cache and job queue setup
2. **Agent Init** - All 5 agents initialized in parallel
3. **Status Check** - Health check across all agents
4. **Project Creation** - Demo project structure
5. **Clip Addition** - Multiple clips added in parallel
6. **Parallel Ops** - Concurrent storyboard operations

### Storyboard.json

The generated `storyboard.json` shows:
```json
{
  "version": "1.2",
  "projectId": "proj_demo_20250101_120000",
  "outputSettings": {...},
  "timeline": [
    {
      "clipId": "clip_001",
      "status": "pending",
      "motionPrompt": "camera slowly pans from left to right",
      ...
    }
  ]
}
```

## Next Steps

After running the examples:

1. **Inspect the storyboard:**
   ```bash
   cat projects/proj_*/storyboard.json | jq
   ```

2. **Check cache status:**
   ```bash
   ls -lh cache/
   ```

3. **Try modifying prompts:**
   - Edit the clip prompts in the demo
   - Re-run to see parallel processing

4. **Integrate AI models:**
   - Add Runway/Stability AI API keys
   - Uncomment production config
   - Run full generation pipeline

## Troubleshooting

### Module Import Errors

Ensure you're running from the repository root:
```bash
cd /path/to/Jynco
python examples/parallel_initialization_demo.py
```

### Missing Directories

The examples will auto-create necessary directories. If you get permission errors:
```bash
mkdir -p projects cache temp logs
chmod 755 projects cache temp logs
```

### Configuration Issues

Verify config files exist:
```bash
ls config/
# Should show: development.json production.json
```

## Performance Notes

The parallel initialization demo showcases:
- **5 agents** initialized concurrently
- **5 clips** added in parallel
- **Multiple status checks** running simultaneously

Typical execution time:
- Infrastructure init: < 100ms
- Agent initialization: < 500ms
- Project creation: < 200ms
- Parallel operations: < 300ms
- **Total: ~1 second**

This demonstrates the async-first design enabling efficient parallel processing.

## Advanced Usage

### Custom Configuration

```python
from src.core import init_config

# Load custom config
init_config(config_path="./my_config.json")
```

### Agent Coordination

```python
# Wire agents manually
architect = ArchitectAgent(...)
architect.set_storyboard_agent(storyboard_agent)
architect.set_motion_agent(motion_agent)

# Run coordinated workflow
result = await architect.execute({
    "operation": "generate_project",
    "projectId": "my_project"
})
```

### Monitoring

```python
# Check all agent status
for name, agent in agents.items():
    status = agent.get_status()
    print(f"{name}: {status['status']}")
```

## Contributing Examples

To add a new example:

1. Create `examples/my_example.py`
2. Add docstring explaining the example
3. Update this README with description
4. Test with: `python examples/my_example.py`
5. Submit PR

## Related Documentation

- [Getting Started Guide](../docs/GETTING_STARTED.md)
- [Architecture Overview](../docs/ARCHITECTURE.md)
- [Agent Documentation](../src/agents/)
- [Schema Reference](../src/schemas/)
