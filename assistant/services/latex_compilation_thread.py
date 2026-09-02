import os
import queue
import subprocess

from PySide6.QtCore import QThread, Signal

MAX_PARALLEL_COMPILATIONS = 4


class LatexCompilationThread(QThread):
    """Compile une liste de fichiers LaTeX en arrière-plan.

    Au plus MAX_PARALLEL_COMPILATIONS processus latexmk tournent simultanément.
    Dès qu'un processus se termine, le suivant en file démarre automatiquement.
    """

    compilation_started = Signal(str)        # nom de fichier (basename)
    compilation_finished = Signal(str, bool) # nom de fichier, succès
    progress = Signal(int, int)              # terminés, total
    all_finished = Signal()

    def __init__(self, tasks: list, parent=None):
        """
        tasks : liste de tuples (chemin_absolu_tex, cwd)
        """
        super().__init__(parent)
        self._tasks = list(tasks)
        self._stop_requested = False

    def request_stop(self):
        """Demande l'arrêt propre : termine les processus en cours et vide la file."""
        self._stop_requested = True

    def run(self):
        task_queue = queue.Queue()
        for task in self._tasks:
            task_queue.put(task)

        total = len(self._tasks)
        done = 0
        active = {}  # tex_file -> Popen

        while True:
            if self._stop_requested:
                for proc in active.values():
                    proc.terminate()
                break

            # Vérifie les processus terminés
            finished_files = [f for f, p in list(active.items()) if p.poll() is not None]
            for tex_file in finished_files:
                proc = active.pop(tex_file)
                success = proc.returncode == 0
                done += 1
                self.compilation_finished.emit(os.path.basename(tex_file), success)
                self.progress.emit(done, total)

            # Lance de nouveaux processus jusqu'à la limite
            while len(active) < MAX_PARALLEL_COMPILATIONS and not task_queue.empty():
                try:
                    tex_file, cwd = task_queue.get_nowait()
                except queue.Empty:
                    break
                self.compilation_started.emit(os.path.basename(tex_file))
                proc = subprocess.Popen(
                    [
                        "latexmk",
                        "-lualatex",
                        "-interaction=nonstopmode",
                        "-file-line-error",
                        "-shell-escape",
                        "-recorder",
                        "-synctex=1",
                        os.path.basename(tex_file),
                    ],
                    cwd=cwd,
                    text=True,
                )
                active[tex_file] = proc

            if task_queue.empty() and not active:
                self.all_finished.emit()
                break

            self.msleep(200)
