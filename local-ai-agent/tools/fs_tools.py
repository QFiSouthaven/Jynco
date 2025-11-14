"""
File system automation tools for the Local AI Agent.
Provides async functions for safe file system operations.
"""

from pathlib import Path
import asyncio
import os
from typing import Dict, Any


async def list_directory(path: str) -> Dict[str, Any]:
    """
    Lists contents of a directory, with security checks.

    Only allows access to paths within PROJECT_ROOT to prevent
    directory traversal attacks.

    Args:
        path: Directory path to list

    Returns:
        dict: Directory contents or error
    """

    def blocking_list_dir():
        try:
            p = Path(path).resolve()  # Get canonical absolute path
            if not p.is_dir():
                return {
                    "error": f"Path '{path}' is not a valid directory or does not exist."
                }

            # CRITICAL SECURITY CHECK: Prevent directory traversal
            allowed_root = Path(os.getenv("PROJECT_ROOT", ".")).resolve()

            # Ensure path is within allowed root
            if not (str(p).startswith(str(allowed_root)) or p == allowed_root):
                return {
                    "error": f"Access denied. Path '{path}' is outside the allowed project root: '{allowed_root}'."
                }

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
