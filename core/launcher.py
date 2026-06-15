import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

HOST = os.getenv("EXAMCELL_HOST", "127.0.0.1")
PORT = int(os.getenv("EXAMCELL_PORT", "8000"))
URL = f"http://{HOST}:{PORT}"

FROZEN = getattr(sys, "frozen", False)

APP_DIR = (
    Path(sys.executable).resolve().parent
    if FROZEN
    else Path(__file__).resolve().parent
)

BUNDLE_DIR = (
    Path(sys._MEIPASS).resolve()
    if FROZEN
    else APP_DIR.parent
)

RUNTIME_DATA_ROOT = APP_DIR / "runtime_data"
MEDIA_ROOT = APP_DIR / "media"

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings"
)

os.environ["EXAMCELL_MODE"] = "standalone"
os.environ["USE_SQLITE"] = "True"
os.environ["DEBUG"] = "False"
os.environ["PYTHON_DOTENV_DISABLED"] = "1"

os.environ.setdefault(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost"
)

os.environ["RUNTIME_DATA_ROOT"] = str(
    RUNTIME_DATA_ROOT
)

os.environ["MEDIA_ROOT"] = str(
    MEDIA_ROOT
)


def ensure_runtime_dirs():
    for path in [
        RUNTIME_DATA_ROOT / "input",
        RUNTIME_DATA_ROOT / "output",
        MEDIA_ROOT,
    ]:
        path.mkdir(
            parents=True,
            exist_ok=True
        )


def port_in_use(host, port):
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as sock:
        return sock.connect_ex((host, port)) == 0


def validate_bundle(settings):
    required_paths = [
        settings.STANDALONE_STATIC_DIR,
        settings.TEMPLATE_DIR,
    ]

    missing_paths = [
        path
        for path in required_paths
        if not Path(path).exists()
    ]

    if missing_paths:
        missing = ", ".join(
            str(path)
            for path in missing_paths
        )

        raise RuntimeError(
            f"ExamCell bundle is incomplete. Missing: {missing}"
        )


def open_browser_when_ready():
    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(
                (HOST, PORT),
                timeout=0.5
            ):
                webbrowser.open(URL)
                return

        except OSError:
            time.sleep(0.25)

    print(
        f"ExamCell server did not become reachable at {URL}",
        flush=True
    )


def print_runtime_config(settings):
    print("=" * 60, flush=True)
    print("ExamCell standalone runtime", flush=True)
    print(f"FROZEN = {FROZEN}", flush=True)
    print(f"APP_DIR = {APP_DIR}", flush=True)
    print(f"BUNDLE_DIR = {BUNDLE_DIR}", flush=True)
    print(f"STATIC_DIR = {settings.STANDALONE_STATIC_DIR}", flush=True)
    print(f"TEMPLATE_DIR = {settings.TEMPLATE_DIR}", flush=True)
    print(f"MEDIA_ROOT = {settings.MEDIA_ROOT}", flush=True)
    print(
        f"DATABASE = {settings.DATABASES['default']['NAME']}",
        flush=True
    )
    print("=" * 60, flush=True)


def main():

    if port_in_use(HOST, PORT):
        print(
            f"ExamCell is already running at {URL}",
            flush=True
        )

        webbrowser.open(URL)
        return

    ensure_runtime_dirs()

    import django
    django.setup()

    from django.conf import settings
    from django.core.management import (
        call_command,
        execute_from_command_line,
    )

    validate_bundle(settings)

    print_runtime_config(settings)

    db_file = Path(
        settings.DATABASES["default"]["NAME"]
    )

    if not db_file.exists():
        print(
            "First launch detected. Creating SQLite database...",
            flush=True
        )
    else:
        print(
            "Applying database migrations...",
            flush=True
        )

    try:
        call_command(
            "migrate",
            interactive=False,
            run_syncdb=True,
        )

    except Exception as exc:
        print(
            f"Migration failed: {exc}",
            flush=True
        )
        raise

    threading.Thread(
        target=open_browser_when_ready,
        daemon=True,
    ).start()

    execute_from_command_line(
        [
            "launcher",
            "runserver",
            f"{HOST}:{PORT}",
            "--noreload",
        ]
    )


if __name__ == "__main__":
    main()