# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json
import aiohttp
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool, Part

# Import our custom modules
from security import verify_token
from tools import git_tools, docker_tools, fs_tools

load_dotenv()

app = FastAPI(
    title="Secure Local AI Agent",
    description="An API for orchestrating local system tasks via a state-aware LLM.",
    version="1.0.0"
)

# --- Strict CORS Configuration ---
# This whitelist defines the ONLY origins allowed to communicate with this API. All others are rejected.
origins = [
    "http://localhost:3000",  # The default URL for the Create React App development server
    "http://127.0.0.1:3000",  # Browsers sometimes resolve localhost to its IP address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Enforce the strict whitelist
    allow_credentials=True,      # Permit requests to include credentials like our Authorization header
    allow_methods=["GET", "POST"],  # Explicitly define the only allowed HTTP methods
    allow_headers=["Authorization", "Content-Type"],  # Explicitly define the only allowed request headers
)

@app.get("/")
async def root():
    return {"message": "Local Agent is running. Status: OK."}


# --- Pydantic Models for Request Bodies ---

class ContainerRequest(BaseModel):
    container_name_or_id: str = Field(..., description="The name or short ID of the Docker container.")

class RepoPathRequest(BaseModel):
    repo_path: str = Field(..., description="The absolute local path to the Git repository.")

class CommitRequest(BaseModel):
    repo_path: str = Field(..., description="The absolute local path to the Git repository.")
    message: str = Field(..., min_length=5, description="The commit message, must be at least 5 characters.")


# --- Tool API Endpoints ---
# This section serves as the agent's public interface for its capabilities.
# Each endpoint is a discrete action, protected and validated.

@app.get("/api/tools/git/status", dependencies=[Depends(verify_token)], tags=["Git Tools"])
async def get_git_status_api():
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise HTTPException(status_code=400, detail="PROJECT_ROOT environment variable not set.")
    return await git_tools.check_all_repo_statuses(project_root)

@app.post("/api/tools/git/clean", dependencies=[Depends(verify_token)], tags=["Git Tools"])
async def clean_git_repo_api(request: RepoPathRequest):
    return await git_tools.clean_repo(request.repo_path)

@app.post("/api/tools/git/commit", dependencies=[Depends(verify_token)], tags=["Git Tools"])
async def commit_changes_api(request: CommitRequest):
    return await git_tools.commit_changes(request.repo_path, request.message)

@app.get("/api/tools/docker/list", dependencies=[Depends(verify_token)], tags=["Docker Tools"])
async def get_docker_list_api(all: bool = False):
    return await docker_tools.list_containers(all)

@app.post("/api/tools/docker/start", dependencies=[Depends(verify_token)], tags=["Docker Tools"])
async def start_docker_container_api(request: ContainerRequest):
    return await docker_tools.start_container(request.container_name_or_id)

@app.get("/api/tools/fs/list", dependencies=[Depends(verify_token)], tags=["File System Tools"])
async def list_directory_api(path: str):
    return await fs_tools.list_directory(path)


# --- Gemini and Orchestrator Setup ---

# Configure the Gemini client using the API key from our secure .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# A simple in-memory chat history. Perfect for a single-user local app.
chat_history = []

# --- Tool Definitions (Schemas for the LLM) ---
# The quality of these descriptions is PARAMOUNT. The LLM's decision-making
# hinges entirely on how well these descriptions articulate the tool's purpose and parameters.

get_git_status_func = FunctionDeclaration(
    name="get_all_git_repo_statuses",
    description="Scans the predefined project directory and gets a detailed git status for all repositories within it. Use this to check for uncommitted changes or untracked files before taking action.",
    parameters={"type": "object", "properties": {}}
)

clean_repo_func = FunctionDeclaration(
    name="clean_git_repository",
    description="HIGHLY DESTRUCTIVE: Executes 'git clean -fdx' on a repository, permanently deleting all untracked files and directories. You absolutely must ask for explicit user confirmation before even suggesting the use of this tool.",
    parameters={"type": "object", "properties": {"repo_path": {"type": "string", "description": "The absolute path to the specific Git repository to clean."}}, "required": ["repo_path"]}
)

commit_changes_func = FunctionDeclaration(
    name="commit_all_changes_in_repo",
    description="Stages all modified and new files ('git add .') and commits them with a given message. Only use this if the 'get_all_git_repo_statuses' tool shows that a repository is dirty.",
    parameters={"type": "object", "properties": {"repo_path": {"type": "string", "description": "The absolute path to the Git repository."}, "message": {"type": "string", "description": "The descriptive commit message."}}, "required": ["repo_path", "message"]}
)

list_docker_containers_func = FunctionDeclaration(
    name="list_docker_containers",
    description="Lists Docker containers on the local machine. By default, it lists only currently running containers. Use the 'all=true' parameter to list all containers, including stopped ones.",
    parameters={"type": "object", "properties": {"all": {"type": "boolean", "description": "Set to true to list all containers, not just the running ones."}}}
)

start_docker_container_func = FunctionDeclaration(
    name="start_docker_container",
    description="Starts a currently stopped Docker container using its name or ID. Should only be used if 'list_docker_containers' shows the container's status is 'exited' or 'created'.",
    parameters={"type": "object", "properties": {"container_name_or_id": {"type": "string", "description": "The name or unique ID of the container to start."}}, "required": ["container_name_or_id"]}
)

list_directory_func = FunctionDeclaration(
    name="list_directory_contents",
    description="Lists the files and subdirectories within a specified local directory path. Useful for exploring the project structure.",
    parameters={"type": "object", "properties": {"path": {"type": "string", "description": "The absolute path of the directory to inspect."}}, "required": ["path"]}
)

# Bundle all of our function declarations into a single, cohesive Tool object for the model
agent_tools = Tool(function_declarations=[
    get_git_status_func, clean_repo_func, commit_changes_func,
    list_docker_containers_func, start_docker_container_func, list_directory_func,
])

# Initialize the Gemini model, equipping it with our custom-defined tools
model = genai.GenerativeModel(model_name="gemini-1.5-pro", tools=[agent_tools])


# --- Helper Function: Execute Tool ---

async def execute_tool(function_call):
    tool_name = function_call.name
    tool_args = dict(function_call.args)  # Convert Gemini's args to a standard Python dict

    INTERNAL_AGENT_TOKEN = os.getenv("AGENT_SECRET_TOKEN")
    headers = {"Authorization": f"Bearer {INTERNAL_AGENT_TOKEN}", "Content-Type": "application/json"}
    base_url = "http://127.0.0.1:8000"  # The agent securely calls its own API

    # A mapping that connects the LLM's vocabulary to our concrete API endpoints
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
    method = tool_config['method']

    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=tool_args) as resp:
                    resp.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                    return await resp.json()
            elif method == "POST":
                async with session.post(url, headers=headers, json=tool_args) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            else:
                return {"error": f"Unsupported HTTP method '{method}' for tool '{tool_name}'."}
    except Exception as e:
        return {"error": f"An error occurred while executing tool '{tool_name}': {str(e)}"}


# --- Chat Endpoint (Full Orchestration Logic) ---

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse, tags=["AI Orchestrator"])
async def chat(request: ChatRequest):
    global chat_history
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise HTTPException(status_code=500, detail="CRITICAL: PROJECT_ROOT env var not set.")

    try:
        # === Step A: Proactively Gather State Snapshot ===
        # This is the agent's "situational awareness." It gathers fresh context BEFORE talking to the LLM.
        git_status_snapshot = await git_tools.check_all_repo_statuses(project_root)
        docker_snapshot = await docker_tools.list_containers(all=True)
        state_snapshot = {
            "git_repositories": git_status_snapshot,
            "docker_containers": docker_snapshot
        }
        state_json = json.dumps(state_snapshot, indent=2)

        # === Step B: Construct a Dynamic System Prompt ===
        # This powerful prompt "grounds" the LLM in the current reality of the local system, every time.
        system_prompt = f"""
You are a senior developer automation assistant operating on a local machine.
You MUST use the following real-time system state snapshot to make all decisions.
Do NOT suggest actions that are redundant (e.g., starting an already running container).
If a destructive action like cleaning a repository is requested, you must reply by asking for explicit confirmation first.

--- System State Snapshot (Captured Moments Ago) ---
{state_json}
--- End Snapshot ---
"""
        
        # Start a new chat session for this turn, loading it with past history.
        chat_session = model.start_chat(history=chat_history)
        
        # Prepend our dynamic system prompt to the user's actual query for maximum context.
        full_prompt = f"{system_prompt}\n\nUser query: {request.prompt}"

        # === Step 1: Send the rich prompt to Gemini ===
        response = await chat_session.send_message_async(full_prompt)

        # Update history with the user's prompt and the model's initial response (which might be a tool call).
        chat_history.append({"role": "user", "parts": [request.prompt]})
        chat_history.append(response.candidates[0].content)

        # === Step 2: Intelligently check if the LLM requested a tool call ===
        part = response.parts[0]
        if part.function_call:
            function_call = part.function_call
            print(f"INFO: LLM requested tool: {function_call.name} with args: {dict(function_call.args)}")

            # === Step 3: Execute the requested tool securely ===
            tool_response_json = await execute_tool(function_call)
            print(f"INFO: Tool execution result: {tool_response_json}")

            # === Step 4: Send the tool's result back to Gemini for final summarization ===
            response_with_tool_result = await chat_session.send_message_async(
                Part.from_function_response(name=function_call.name, response=tool_response_json)
            )
            
            # Update history with the tool's raw output and the model's final, human-readable summary.
            chat_history.append({"role": "tool", "parts": [Part.from_function_response(name=function_call.name, response=tool_response_json)]})
            chat_history.append(response_with_tool_result.candidates[0].content)
            
            final_text_response = response_with_tool_result.parts[0].text
            return ChatResponse(response=final_text_response)
        else:
            # If no tool was called, the model's first response is the final one.
            text_response = part.text
            return ChatResponse(response=text_response)

    except Exception as e:
        print(f"ERROR in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred in the orchestrator: {str(e)}")
