"""
Git automation tools for the Local AI Agent.
Provides async functions for Git repository operations.
"""

import asyncio
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
from typing import Dict, Any


async def check_all_repo_statuses(project_root: str) -> Dict[str, Any]:
    """
    Scans the project root directory and returns Git status for all repositories.

    Args:
        project_root: Absolute path to the project root directory

    Returns:
        dict: Status information for all Git repositories found
    """

    def blocking_git_check():
        root_path = Path(project_root)
        if not root_path.is_dir():
            return {
                "error": f"Invalid project root path: '{project_root}' is not a directory."
            }

        statuses = {}
        # Iterate through subdirectories
        for repo_path in root_path.iterdir():
            if repo_path.is_dir():
                try:
                    repo = Repo(repo_path)
                    statuses[repo_path.name] = {
                        "path": str(repo_path),
                        "is_dirty": repo.is_dirty(untracked_files=True),
                        "untracked_files": repo.untracked_files,
                        "active_branch": (
                            repo.active_branch.name
                            if repo.active_branch
                            else "N/A"  # Handle detached HEAD
                        ),
                    }
                except InvalidGitRepositoryError:
                    # Not a git repo, skip silently
                    continue
                except Exception as e:
                    statuses[repo_path.name] = {
                        "error": str(e),
                        "path": str(repo_path),
                    }
        return statuses

    # Run in thread to prevent blocking the event loop
    return await asyncio.to_thread(blocking_git_check)


async def clean_repo(repo_path: str) -> Dict[str, Any]:
    """
    Executes 'git clean -fdx' to remove all untracked files and directories.

    WARNING: This is a DESTRUCTIVE operation that permanently deletes files.

    Args:
        repo_path: Absolute path to the Git repository

    Returns:
        dict: Operation status and message
    """

    def blocking_git_clean():
        try:
            repo = Repo(repo_path)
            if repo.is_dirty(untracked_files=True):
                # WARNING: Highly destructive - removes all untracked files
                repo.git.clean("-fdx")
                return {
                    "status": "success",
                    "message": f"Repository '{repo_path}' has been forcefully cleaned, removing all untracked files and directories.",
                }
            else:
                return {
                    "status": "no_action",
                    "message": f"Repository '{repo_path}' is already clean.",
                }
        except InvalidGitRepositoryError:
            return {
                "status": "error",
                "message": f"Path '{repo_path}' is not a valid Git repository.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred during git clean: {str(e)}",
            }

    return await asyncio.to_thread(blocking_git_clean)


async def commit_changes(repo_path: str, message: str) -> Dict[str, Any]:
    """
    Stages all changes and commits them with the provided message.

    Args:
        repo_path: Absolute path to the Git repository
        message: Commit message

    Returns:
        dict: Operation status and message
    """

    def blocking_git_commit():
        try:
            repo = Repo(repo_path)
            if not repo.is_dirty(untracked_files=True):
                return {
                    "status": "no_action",
                    "message": f"No changes to commit in '{repo_path}'.",
                }

            # Stage all changes including new files
            repo.git.add(A=True)
            repo.index.commit(message)
            return {
                "status": "success",
                "message": f"Changes committed in '{repo_path}' with message: '{message}'.",
            }
        except InvalidGitRepositoryError:
            return {
                "status": "error",
                "message": f"Path '{repo_path}' is not a valid Git repository.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred during git commit: {str(e)}",
            }

    return await asyncio.to_thread(blocking_git_commit)
