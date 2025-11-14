# tools/git_tools.py
import asyncio
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
import os

# NOTE: The use of `asyncio.to_thread` is paramount. The `GitPython` library is
# synchronous (blocking) by nature. Running its operations in a separate thread
# prevents the entire FastAPI server from stalling while waiting for a Git command to complete.

async def check_all_repo_statuses(project_root: str):
    def blocking_git_check():
        root_path = Path(project_root)
        if not root_path.is_dir():
            return {"error": f"Invalid project root path: '{project_root}' is not a directory."}

        statuses = {}
        # Intelligently iterate through subdirectories of the project root
        for repo_path in root_path.iterdir():
            if repo_path.is_dir():
                try:
                    repo = Repo(repo_path)
                    statuses[repo_path.name] = {
                        "path": str(repo_path),
                        "is_dirty": repo.is_dirty(untracked_files=True),  # A more comprehensive check
                        "untracked_files": repo.untracked_files,
                        "active_branch": repo.active_branch.name if repo.active_branch else "N/A"  # Handle detached HEAD
                    }
                except InvalidGitRepositoryError:
                    # This directory is not a git repo, so we gracefully and silently skip it.
                    continue
                except Exception as e:
                    statuses[repo_path.name] = {"error": str(e), "path": str(repo_path)}
        return statuses
    return await asyncio.to_thread(blocking_git_check)

async def clean_repo(repo_path: str):
    def blocking_git_clean():
        try:
            repo = Repo(repo_path)
            if repo.is_dirty(untracked_files=True):
                # WARNING: This is a highly destructive command. The LLM's prompt
                # engineering must ensure user confirmation is received before calling this.
                repo.git.clean('-fdx')  # -x removes ignored files, -d removes directories
                return {"status": "success", "message": f"Repository '{repo_path}' has been forcefully cleaned, removing all untracked files and directories."}
            else:
                return {"status": "no_action", "message": f"Repository '{repo_path}' is already clean."}
        except InvalidGitRepositoryError:
            return {"status": "error", "message": f"Path '{repo_path}' is not a valid Git repository."}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred during git clean: {str(e)}"}
    return await asyncio.to_thread(blocking_git_clean)

async def commit_changes(repo_path: str, message: str):
    def blocking_git_commit():
        try:
            repo = Repo(repo_path)
            if not repo.is_dirty(untracked_files=True):
                return {"status": "no_action", "message": f"No changes to commit in '{repo_path}'."}

            repo.git.add(A=True)  # Stage all changes, including new files
            repo.index.commit(message)
            return {"status": "success", "message": f"Changes committed in '{repo_path}' with message: '{message}'."}
        except InvalidGitRepositoryError:
            return {"status": "error", "message": f"Path '{repo_path}' is not a valid Git repository."}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred during git commit: {str(e)}"}
    return await asyncio.to_thread(blocking_git_commit)
