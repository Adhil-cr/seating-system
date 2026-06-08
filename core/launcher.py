import os
import threading
import webbrowser
from pathlib import Path
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ["USE_SQLITE"] = "True"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# Runtime paths
os.environ["RUNTIME_DATA_ROOT"] = str(
    BASE_DIR / "runtime_data"
)

os.environ["MEDIA_ROOT"] = str(
    BASE_DIR / "media"
)

# Create folders automatically
(BASE_DIR / "runtime_data" / "input").mkdir(
    parents=True,
    exist_ok=True
)

(BASE_DIR / "runtime_data" / "output").mkdir(
    parents=True,
    exist_ok=True
)

(BASE_DIR / "media").mkdir(
    parents=True,
    exist_ok=True
)

# Django imports AFTER env vars
import django
django.setup()

from django.core.management import call_command
from django.core.management import execute_from_command_line

# ----------------------------------
# First-run database initialization
# ----------------------------------

db_file = BASE_DIR / "examcell.sqlite3"

if not db_file.exists():
    print("First launch detected.")
    print("Creating SQLite database...")

    call_command(
        "migrate",
        interactive=False,
        run_syncdb=True
    )

    print("Database initialized successfully.")

# ----------------------------------
# Launch browser
# ----------------------------------

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

threading.Timer(3, open_browser).start()

# ----------------------------------
# Start Django server
# ----------------------------------

execute_from_command_line([
    "manage.py",
    "runserver",
    "127.0.0.1:8000",
    "--noreload",
])