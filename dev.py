"""Dev helper: lance le backend (uvicorn --reload) et le serveur frontend (livereload)
Usage: python dev.py
Assure-toi d'avoir installé les dépendances (backend + frontend) dans ton venv.
"""
import subprocess
import sys
import os
import signal


def start_process(cmd, cwd=None):
    # Start subprocess with universal newlines for readable output
    return subprocess.Popen(cmd, cwd=cwd, shell=False)


def main():
    root = os.path.dirname(__file__)

    # Prefer python from .venv if present, otherwise use current interpreter
    venv_python = os.path.join(root, '.venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        python = venv_python
    else:
        python = sys.executable

    # Commands (use absolute paths)
    backend_cmd = [python, '-m', 'uvicorn', 'backend.main:app', '--reload', '--port', '8001']
    frontend_script = os.path.join(root, 'frontend', 'serve.py')
    frontend_cmd = [python, frontend_script]

    procs = []
    try:
        print('Starting backend: ', ' '.join(backend_cmd))
        p1 = start_process(backend_cmd, cwd=root)
        procs.append(p1)

        print('Starting frontend livereload: ', ' '.join(frontend_cmd))
        p2 = start_process(frontend_cmd, cwd=root)
        procs.append(p2)

        # Forward output until interrupted
        while True:
            for p in procs:
                ret = p.poll()
                if ret is not None:
                    print(f'Process {p.args} exited with {ret}')
                    # If one process exits, continue monitoring others
            try:
                # wait a bit
                import time
                time.sleep(0.5)
            except KeyboardInterrupt:
                raise
    except KeyboardInterrupt:
        print('\nShutting down subprocesses...')
        for p in procs:
            try:
                p.send_signal(signal.SIGINT)
            except Exception:
                try:
                    p.terminate()
                except Exception:
                    pass
        for p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        print('Stopped.')


if __name__ == '__main__':
    main()
