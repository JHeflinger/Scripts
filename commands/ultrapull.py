"""
author: Jason Heflinger
description: Pulls all git repos in a given directory and prints out success/failure 
"""

import os
import sys
import subprocess
from pathlib import Path

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()

def git_pull(repo_path: Path):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "pull"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            return "SUCCESS", output
        conflict_strings = [
            "CONFLICT",
            "Automatic merge failed",
            "fix conflicts",
        ]
        if any(s in output for s in conflict_strings):
            return "CONFLICT", output
        return "FAILED", output
    except Exception as e:
        return "FAILED", str(e)

def color_status(status):
    if status == "SUCCESS":
        return f"{GREEN}{status}{RESET}"
    elif status == "CONFLICT":
        return f"{YELLOW}{status}{RESET}"
    else:
        return f"{RED}{status}{RESET}"

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    if not root.is_dir():
        print(f"{RED}Error:{RESET} '{root}' is not a directory")
        sys.exit(1)
    results = []
    print(f"{BLUE}Scanning:{RESET} {root}\n")
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if not is_git_repo(entry):
            continue
        print(f"Pulling {entry.name}...")
        status, output = git_pull(entry)
        results.append((entry.name, status))
        print(f"  {color_status(status)}")
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    success_count = 0
    conflict_count = 0
    failed_count = 0
    for repo, status in results:
        print(f"{repo:<40} {color_status(status)}")
        if status == "SUCCESS":
            success_count += 1
        elif status == "CONFLICT":
            conflict_count += 1
        else:
            failed_count += 1
    print("\nTotals:")
    print(f"  {GREEN}Success:{RESET}  {success_count}")
    print(f"  {YELLOW}Conflict:{RESET} {conflict_count}")
    print(f"  {RED}Failed:{RESET}   {failed_count}")

if __name__ == "__main__":
    main()
