#!/usr/bin/env python3
"""
Setup script for Local AI Agent
Generates secure tokens and creates .env file
"""

import secrets
import os
from pathlib import Path


def generate_secret_token():
    """Generate a cryptographically secure token"""
    return secrets.token_hex(32)


def create_env_file():
    """Create .env file with generated secrets"""
    env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Setup cancelled.")
            return

    print("🔐 Generating secure token...")
    token = generate_secret_token()

    print("\n📝 Please provide the following information:")
    gemini_key = input("Enter your Gemini API key (from https://ai.google.dev/): ").strip()

    default_project_root = str(Path.home() / "projects")
    project_root = (
        input(f"Enter PROJECT_ROOT path (default: {default_project_root}): ").strip()
        or default_project_root
    )

    env_content = f"""# Gemini API Configuration
GEMINI_API_KEY={gemini_key}

# Agent Security Token (auto-generated)
AGENT_SECRET_TOKEN={token}

# Project Root - The sandbox directory where the agent can operate
PROJECT_ROOT={project_root}
"""

    with open(env_path, "w") as f:
        f.write(env_content)

    print(f"\n✅ .env file created successfully!")
    print(f"   Token: {token[:16]}... (saved to .env)")
    print(f"   Project Root: {project_root}")
    print("\n⚠️  IMPORTANT: Keep your .env file secure and never commit it to git!")
    print("   The .gitignore file has been configured to exclude it.")
    print("\n🚀 Next steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Start the backend: uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
    print("   3. Set up the frontend (see FRONTEND_SETUP.md)")


if __name__ == "__main__":
    create_env_file()
