import os
import platform
import subprocess
from pathlib import Path


class ProcessService:

    @staticmethod
    def open_file_default(file_path: str) -> None:
        system = platform.system()

        if system == "Windows":
            os.startfile(file_path)

        elif system == "Darwin":
            subprocess.run(["open", file_path], check=False)

        else:
            subprocess.run(["xdg-open", file_path], check=False)
    
    @staticmethod
    def open_with(app: str | Path, file: str | Path, *args) -> None:
        subprocess.Popen([str(app)] + list(args) + [str(file)])