#!/usr/bin/env python3
"""Auto-deploy hook: copies edited Python source files to the Docker container.

Triggered by PostToolUse on Edit/Write. Only acts on files under src/alejandria/.
Restarts the container only if files were actually copied.
"""

import json
import os
import subprocess
import sys


def main():
    # Read the tool use event from stdin
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        return

    # Extract the file path from the tool input
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return

    # Normalize path separators
    file_path = file_path.replace("\\", "/")

    # Only deploy src/alejandria/ Python files
    if "/src/alejandria/" not in file_path or not file_path.endswith(".py"):
        return

    # Extract the relative path from src/ onward
    idx = file_path.find("/src/alejandria/")
    if idx < 0:
        return
    relative = file_path[idx + 1:]  # e.g., "src/alejandria/chat/rag.py"
    container_path = f"/app/{relative}"

    # Check if container is running
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", "alejandria-api"],
            capture_output=True, text=True, timeout=5,
        )
        if "true" not in result.stdout.lower():
            return
    except Exception:
        return

    # Copy file to container
    try:
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        subprocess.run(
            ["docker", "cp", file_path, f"alejandria-api:{container_path}"],
            capture_output=True, text=True, timeout=10, env=env,
        )
        print(f"[auto-deploy] Copied {relative} to container", file=sys.stderr)
    except Exception as e:
        print(f"[auto-deploy] Copy failed: {e}", file=sys.stderr)
        return

    # Restart container to pick up changes
    try:
        subprocess.run(
            ["docker", "restart", "alejandria-api"],
            capture_output=True, text=True, timeout=30,
        )
        print("[auto-deploy] Container restarted", file=sys.stderr)
    except Exception as e:
        print(f"[auto-deploy] Restart failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
