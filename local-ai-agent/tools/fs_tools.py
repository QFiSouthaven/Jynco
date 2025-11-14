# tools/fs_tools.py
from pathlib import Path
import asyncio
import os

async def list_directory(path: str):
    def blocking_list_dir():
        try:
            p = Path(path).resolve()  # .resolve() gets the canonical, absolute path
            if not p.is_dir():
                return {"error": f"Path '{path}' is not a valid directory or does not exist."}
            
            # A crucial security check to prevent directory traversal attacks (e.g., asking for /root)
            # This ensures the agent can only "see" within its designated project root.
            allowed_root = Path(os.getenv("PROJECT_ROOT", ".")).resolve()
            # Ensure the path is either the root itself or a subpath of the root.
            # Use str(p) to compare string representations for paths correctly.
            if not (str(p).startswith(str(allowed_root)) or p == allowed_root):
                return {"error": f"Access denied. Path '{path}' is outside the allowed project root: '{allowed_root}'."}

            items = {"directories": [], "files": []}
            for item in p.iterdir():
                if item.is_dir():
                    items["directories"].append(item.name)
                else:
                    items["files"].append(item.name)
            return items
        except Exception as e:
            return {"error": f"Failed to list directory '{path}': {str(e)}"}
    return await asyncio.to_thread(blocking_list_dir)
