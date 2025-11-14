"""
Docker automation tools for the Local AI Agent.
Provides async functions for Docker container management.
"""

import docker
import asyncio
from docker.errors import NotFound, APIError
from typing import Dict, Any, List


# Initialize Docker client (can raise exception if Docker isn't running)
try:
    client = docker.from_env()
except Exception as e:
    print(
        f"WARNING: Could not connect to Docker daemon: {e}. "
        "Docker tools will be unavailable."
    )
    client = None


async def list_containers(all_containers: bool = False) -> List[Dict[str, Any]] | Dict[str, str]:
    """
    Lists Docker containers on the local machine.

    Args:
        all_containers: If True, includes stopped containers

    Returns:
        list: Container information or error dict
    """

    def blocking_docker_list():
        if not client:
            return {
                "error": "Docker client not initialized. Is the Docker daemon running?"
            }
        try:
            containers = client.containers.list(all=all_containers)
            return [
                {
                    "id": c.short_id,
                    "name": c.name,
                    "image": str(c.image.tags[0]) if c.image.tags else "N/A",
                    "status": c.status,
                }
                for c in containers
            ]
        except APIError as e:
            return {"error": f"Docker API error: {str(e)}"}
        except Exception as e:
            return {
                "error": f"An unexpected error occurred while listing containers: {str(e)}"
            }

    return await asyncio.to_thread(blocking_docker_list)


async def start_container(container_name_or_id: str) -> Dict[str, Any]:
    """
    Starts a stopped Docker container.

    Args:
        container_name_or_id: Container name or ID

    Returns:
        dict: Operation status and message
    """

    def blocking_docker_start():
        if not client:
            return {
                "error": "Docker client not initialized. Is the Docker daemon running?"
            }
        try:
            container = client.containers.get(container_name_or_id)
            if container.status == "running":
                return {
                    "status": "no_action",
                    "message": f"Container '{container.name}' is already running.",
                }

            container.start()
            container.reload()  # Refresh status
            return {
                "status": "success",
                "message": f"Container '{container.name}' started successfully. New status: {container.status}",
            }
        except NotFound:
            return {
                "status": "error",
                "message": f"Container '{container_name_or_id}' not found.",
            }
        except APIError as e:
            return {
                "status": "error",
                "message": f"Docker API error during start: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred while starting container: {str(e)}",
            }

    return await asyncio.to_thread(blocking_docker_start)
