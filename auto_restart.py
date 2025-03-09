import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

script_to_run = "gui_init.py"  # Change this to your script's filename

class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen([sys.executable, script_to_run])

    def on_modified(self, event):
        if event.src_path.endswith(script_to_run):
            print(f"File {script_to_run} changed, restarting...")
            self.restart_script()

if __name__ == "__main__":
    event_handler = RestartOnChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
