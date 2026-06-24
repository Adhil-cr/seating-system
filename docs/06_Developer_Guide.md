# Developer Guide

## Introduction

This document explains the internal implementation details of the ExamCell Examination Hall Seating Arrangement Automation System.

It is intended for developers, maintainers, contributors, and future project enhancements.

---

# Technology Stack

## Backend

- Python
- Django

## Database

- PostgreSQL
- SQLite

## Frontend

- HTML
- CSS
- JavaScript

## Reporting

- ReportLab
- OpenPyXL

## Deployment

- Render
- PyInstaller

---

# Project Structure

seating-system/
├── core/
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── decorators.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── students/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── exams/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── halls/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── seating/
│   │   ├── algorithms/
│   │   │   ├── csv_normalizer.py
│   │   │   ├── exam_session_preparer.py
│   │   │   ├── seating_allocator.py
│   │   │   └── validators.py
│   │   ├── migrations/
│   │   ├── allocator.py
│   │   ├── allocator_service.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── dashboard/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── utils/
│   │   └── b2_storage.py
│   ├── media/                 # Standalone-mode media
│   ├── runtime_data/
│   │   ├── input/
│   │   └── output/
│   ├── launcher.py
│   ├── launcher.spec
│   ├── manage.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── requirements-build.txt
├── templates/
│   ├── auth/
│   ├── components/
│   ├── dashboard/
│   ├── exams/
│   ├── halls/
│   ├── profile/
│   ├── seating/
│   ├── students/
│   └── base.html
├── static/
│   ├── css/
│   ├── images/
│   ├── js/
│   └── samples/
├── media/                     # Development-mode media
├── docs/
├── .env
└── .gitignore





## Seating Algorithms

The seating allocation engine is implemented inside:

```text
seating/algorithms/
```

### csv_normalizer.py

Responsibilities:

- Read uploaded CSV files
- Validate structure
- Clean data
- Normalize records
- Generate standardized student datasets

---

### validators.py

Responsibilities:

- Validate student records
- Validate subject information
- Detect missing values
- Verify CSV integrity

---

### exam_session_preparer.py

Responsibilities:

- Prepare examination datasets
- Filter students by subjects
- Group students for allocation
- Generate allocation-ready records

---

### seating_allocator.py

Responsibilities:

- Allocate students to halls
- Apply hall capacity rules
- Generate seat assignments
- Enforce allocation constraints

---

### allocator_service.py

Responsibilities:

- Orchestrate the complete allocation pipeline
- Connect normalization, validation, preparation and allocation modules
- Manage runtime files
- Generate outputs






## Deployment Architecture

ExamCell supports three deployment modes.

### Development Mode

```text
Django
PostgreSQL
Local Environment
```

---

### Cloud Deployment

```text
User
   │
Browser
   │
Render
   │
Django
   │
PostgreSQL
   │
Backblaze B2
```

---

## Standalone Deployment

ExamCell supports offline standalone execution on both Linux and Windows operating systems.

### Linux Standalone Architecture

```text
User
   │
Browser
   │
launcher
   │
Django Application
   │
SQLite Database
   │
runtime_data/
media/
```

Features:

- Portable deployment
- No Python installation required
- SQLite database
- Local runtime storage
- Linux executable package

---

### Windows Standalone Architecture

```text
User
   │
Browser
   │
launcher.exe
   │
Django Application
   │
SQLite Database
   │
runtime_data/
media/
```

Features:

- Portable deployment
- No Python installation required
- SQLite database
- Local runtime storage
- Windows executable package

---

### Shared Standalone Features

Both Linux and Windows standalone editions provide:

- Offline operation
- Automatic database initialization
- Automatic migration execution
- Static file serving
- PDF export
- Excel export
- Runtime data persistence
- Browser-based interface
- User account management
- Seating allocation generation

## Cross-Platform Support

| Platform | Status     |
| -------- | ---------- |
| Linux    | Supported  |
| Windows  | Supported  |
| macOS    | Not Tested |

### Linux Build

- PyInstaller
- launcher executable
- TAR.GZ release package

### Windows Build

- PyInstaller
- launcher.exe executable
- ZIP release package
