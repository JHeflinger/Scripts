"""
author: Jason Heflinger
description: takes in a directory to monitor and a script to run. If any files in the directory change,
             the script is run.
"""

import sys
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        super().__init__()
        self.script = script
        self._running = False

    def on_any_event(self, event):
        if self._running:
            return
        self._running = True
        try:
            print(f"\nChange detected: {event.src_path}")
            subprocess.run(self.script, shell=True, check=False)
        except Exception as e:
            print(f"Failed to run script: {e}")
        finally:
            self._running = False

def watch_directory(directory, script):
    path = Path(directory)
    if not path.exists():
        print(f"Directory '{directory}' does not exist.")
        sys.exit(1)
    event_handler = ChangeHandler(script)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    print(f"Monitoring directory: {path.resolve()}")
    print("Press Ctrl+C to stop.\n")
    observer.start()
    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: watchdog <directory> <script>")
        sys.exit(1)

    watch_directory(sys.argv[1], sys.argv[2])
