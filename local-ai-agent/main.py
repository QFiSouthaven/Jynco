"""
Local AI Agent - Main Application
A secure, local-first AI agent with tool execution capabilities.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json
import aiohttp

# Import Google Generative AI
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool, Part

# Import custom modules
from security import verify_token
from tools import git_tools, docker_tools, fs_tools

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Secure Local AI Agent",
    description="An API for orchestrating local system tasks via a state-aware LLM.",
    version="1.0.0",
)

# --- CORS Configuration ---
# Strict whitelist - only allow requests from the frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Gemini Configuration ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Simple in-memory chat history
chat_history = []

# --- Tool Definitions for Gemini ---
# These function declarations teach the LLM what tools are available

get_git_status_func = FunctionDeclaration(
    name="get_all_git_repo_statuses",
    description="Scans the predefined project directory and gets detailed git status for all repositories. Use this to check for uncommitted changes or untracked files before taking action.",
    parameters={"type": "object", "properties": {}},
)

clean_repo_func = FunctionDeclaration(
    name="clean_git_repository",
    description="HIGHLY DESTRUCTIVE: Executes 'git clean -fdx' on a repository, permanently deleting all untracked files and directories. You absolutely must ask for explicit user confirmation before even suggesting the use of this tool.",
    parameters={
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "The absolute path to the specific Git repository to clean.",
            }
        },
        "required": ["repo_path"],
    },
)

commit_changes_func = FunctionDeclaration(
    name="commit_all_changes_in_repo",
    description="Stages all modified and new files ('git add .') and commits them with a given message. Only use this if 'get_all_git_repo_statuses' shows that a repository is dirty.",
    parameters={
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "The absolute path to the Git repository.",
            },
            "message": {"type": "string", "description": "The descriptive commit message."},
        },
        "required": ["repo_path", "message"],
    },
)

list_docker_containers_func = FunctionDeclaration(
    name="list_docker_containers",
    description="Lists Docker containers on the local machine. By default, lists only running containers. Use 'all=true' parameter to list all containers including stopped ones.",
    parameters={
        "type": "object",
        "properties": {
            "all": {
                "type": "boolean",
                "description": "Set to true to list all containers, not just running ones.",
            }
        },
    },
)

start_docker_container_func = FunctionDeclaration(
    name="start_docker_container",
    description="Starts a currently stopped Docker container using its name or ID. Should only be used if 'list_docker_containers' shows the container's status is 'exited' or 'created'.",
    parameters={
        "type": "object",
        "properties": {
            "container_name_or_id": {
                "type": "string",
                "description": "The name or unique ID of the container to start.",
            }
        },
        "required": ["container_name_or_id"],
    },
)

list_directory_func = FunctionDeclaration(
    name="list_directory_contents",
    description="Lists the files and subdirectories within a specified local directory path. Useful for exploring the project structure.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The absolute path of the directory to inspect.",
            }
        },
        "required": ["path"],
    },
)

# Bundle all functions into a Tool object
agent_tools = Tool(
    function_declarations=[
        get_git_status_func,
        clean_repo_func,
        commit_changes_func,
        list_docker_containers_func,
        start_docker_container_func,
        list_directory_func,
    ]
)

# Initialize Gemini model with tools
model = genai.GenerativeModel(model_name="gemini-1.5-pro", tools=[agent_tools])


# --- Pydantic Models ---
class ContainerRequest(BaseModel):
    container_name_or_id: str = Field(
        ..., description="The name or short ID of the Docker container."
    )


class RepoPathRequest(BaseModel):
    repo_path: str = Field(..., description="The absolute local path to the Git repository.")


class CommitRequest(BaseModel):
    repo_path: str = Field(..., description="The absolute local path to the Git repository.")
    message: str = Field(
        ..., min_length=5, description="The commit message, must be at least 5 characters."
    )


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User's chat prompt")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI agent's response")


# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Local AI Agent is running. Status: OK."}


# --- Tool API Endpoints ---
# All endpoints are protected by Bearer token authentication


@app.get("/api/tools/git/status", dependencies=[Depends(verify_token)], tags=["Git Tools"])
async def get_git_status_api():
    """Get Git status for all repositories in PROJECT_ROOT"""
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise HTTPException(status_code=400, detail="PROJECT_ROOT environment variable not set.")
    return await git_tools.check_all_repo_statuses(project_root)


@app.post("/api/tools/git/clean", dependencies=[Depends(verify_token)], tags=["Git Tools"])
async def clean_git_repo_api(request: RepoPathRequest):
    """Clean a Git repository (DESTRUCTIVE: removes all untracked files)"""
    return await git_tools.clean_repo(request.repo_path)


@app.post("/api/tools/git/commit", dependencies=[Depends(verify_token)], tags=["Git Tools"])
async def commit_changes_api(request: CommitRequest):
    """Commit all changes in a Git repository"""
    return await git_tools.commit_changes(request.repo_path, request.message)


@app.get("/api/tools/docker/list", dependencies=[Depends(verify_token)], tags=["Docker Tools"])
async def get_docker_list_api(all: bool = False):
    """List Docker containers"""
    return await docker_tools.list_containers(all)


@app.post(
    "/api/tools/docker/start", dependencies=[Depends(verify_token)], tags=["Docker Tools"]
)
async def start_docker_container_api(request: ContainerRequest):
    """Start a Docker container"""
    return await docker_tools.start_container(request.container_name_or_id)


@app.get("/api/tools/fs/list", dependencies=[Depends(verify_token)], tags=["File System Tools"])
async def list_directory_api(path: str):
    """List directory contents"""
    return await fs_tools.list_directory(path)


# --- AI Orchestrator ---


async def execute_tool(function_call):
    """
    Execute a tool by making an authenticated HTTP call to the local API.

    This creates a secure bridge between the LLM's intent and actual execution.
    """
    tool_name = function_call.name
    tool_args = dict(function_call.args)

    INTERNAL_AGENT_TOKEN = os.getenv("AGENT_SECRET_TOKEN")
    headers = {"Authorization": f"Bearer {INTERNAL_AGENT_TOKEN}", "Content-Type": "application/json"}
    base_url = "http://127.0.0.1:8000"

    # Map LLM function names to API endpoints
    url_map = {
        "get_all_git_repo_statuses": {"method": "GET", "url": "/api/tools/git/status"},
        "clean_git_repository": {"method": "POST", "url": "/api/tools/git/clean"},
        "commit_all_changes_in_repo": {"method": "POST", "url": "/api/tools/git/commit"},
        "list_docker_containers": {"method": "GET", "url": "/api/tools/docker/list"},
        "start_docker_container": {"method": "POST", "url": "/api/tools/docker/start"},
        "list_directory_contents": {"method": "GET", "url": "/api/tools/fs/list"},
    }

    tool_config = url_map.get(tool_name)
    if not tool_config:
        return {"error": f"Tool '{tool_name}' is not recognized or mapped internally."}

    url = f"{base_url}{tool_config['url']}"
    method = tool_config["method"]

    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=tool_args) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            elif method == "POST":
                async with session.post(url, headers=headers, json=tool_args) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            else:
                return {"error": f"Unsupported HTTP method '{method}' for tool '{tool_name}'."}
    except Exception as e:
        return {"error": f"An error occurred while executing tool '{tool_name}': {str(e)}"}


@app.post("/api/chat", response_model=ChatResponse, tags=["AI Orchestrator"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint with AI orchestration.

    This endpoint:
    1. Gathers a real-time state snapshot
    2. Sends prompt + state to Gemini
    3. Executes any tool calls requested by Gemini
    4. Returns the final response to the user
    """
    global chat_history

    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise HTTPException(
            status_code=500, detail="CRITICAL: PROJECT_ROOT env var not set."
        )

    try:
        # === Step A: Gather State Snapshot ===
        # This provides real-time context to the LLM
        git_status_snapshot = await git_tools.check_all_repo_statuses(project_root)
        docker_snapshot = await docker_tools.list_containers(all=True)

        state_snapshot = {
            "git_repositories": git_status_snapshot,
            "docker_containers": docker_snapshot,
        }
        state_json = json.dumps(state_snapshot, indent=2)

        # === Step B: Construct Dynamic System Prompt ===
        system_prompt = f"""
You are a senior developer automation assistant operating on a local machine.
You MUST use the following real-time system state snapshot to make all decisions.
Do NOT suggest actions that are redundant (e.g., starting an already running container).
If a destructive action like cleaning a repository is requested, you must ask for explicit confirmation first.

--- System State Snapshot (Captured Moments Ago) ---
{state_json}
--- End Snapshot ---
"""

        # Start chat session with history
        chat_session = model.start_chat(history=chat_history)

        # Prepend system prompt to user query
        full_prompt = f"{system_prompt}\n\nUser query: {request.prompt}"

        # === Step 1: Send to Gemini ===
        response = await chat_session.send_message_async(full_prompt)

        # Update history
        chat_history.append({"role": "user", "parts": [request.prompt]})
        chat_history.append(response.candidates[0].content)

        # === Step 2: Check for tool calls ===
        part = response.parts[0]
        if part.function_call:
            function_call = part.function_call
            print(f"INFO: LLM requested tool: {function_call.name} with args: {dict(function_call.args)}")

            # === Step 3: Execute tool ===
            tool_response_json = await execute_tool(function_call)
            print(f"INFO: Tool execution result: {tool_response_json}")

            # === Step 4: Send tool result back to Gemini ===
            response_with_tool_result = await chat_session.send_message_async(
                Part.from_function_response(
                    name=function_call.name, response=tool_response_json
                )
            )

            # Update history
            chat_history.append(
                {
                    "role": "tool",
                    "parts": [
                        Part.from_function_response(
                            name=function_call.name, response=tool_response_json
                        )
                    ],
                }
            )
            chat_history.append(response_with_tool_result.candidates[0].content)

            final_text_response = response_with_tool_result.parts[0].text
            return ChatResponse(response=final_text_response)
        else:
            # No tool call, return direct response
            text_response = part.text
            return ChatResponse(response=text_response)

    except Exception as e:
        print(f"ERROR in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred in the orchestrator: {str(e)}",
        )
