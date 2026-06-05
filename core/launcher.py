import os
import threading
import webbrowser
from django.core.management import execute_from_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ["USE_SQLITE"] = "True"


def open_browser():
    webbrowser.open("http://127.0.0.1:8000")


threading.Timer(3, open_browser).start()

execute_from_command_line([
    "manage.py",
    "runserver",
    "127.0.0.1:8000",
    "--noreload"
])

