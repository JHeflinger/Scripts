"""
author: Jason Heflinger
description: Pulls all git repos in a given directory and prints out success/failure 
"""

import sys
import subprocess
from pathlib import Path

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()

def git_pull(repo_path: Path):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            up_to_date_strings = [
                "Already up to date.",
                "Already up-to-date.",
            ]
            if any(s in output for s in up_to_date_strings):
                return "UP_TO_DATE", output
            return "UPDATED", output
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
    if status == "UPDATED":
        return f"{GREEN}{status}{RESET}"
    elif status == "UP_TO_DATE":
        return f"{CYAN}{status}{RESET}"
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
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    updated_count = 0
    up_to_date_count = 0
    conflict_count = 0
    failed_count = 0
    for repo, status in results:
        print(f"{repo:<50} {color_status(status)}")
        if status == "UPDATED":
            updated_count += 1
        elif status == "UP_TO_DATE":
            up_to_date_count += 1
        elif status == "CONFLICT":
            conflict_count += 1
        else:
            failed_count += 1
    print("\nTotals:")
    print(f"  {GREEN}Updated:{RESET}      {updated_count}")
    print(f"  {CYAN}Up To Date:{RESET}   {up_to_date_count}")
    print(f"  {YELLOW}Conflict:{RESET}     {conflict_count}")
    print(f"  {RED}Failed:{RESET}       {failed_count}")

if __name__ == "__main__":
    main()
