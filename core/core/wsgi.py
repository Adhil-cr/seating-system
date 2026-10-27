"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Ensure the core project directory is present in sys.path
CORE_DIR = Path(__file__).resolve().parent.parent
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
