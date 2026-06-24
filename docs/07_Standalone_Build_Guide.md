# Standalone Build Guide

# ExamCell Standalone Build Guide

## Introduction

This document describes the process used to build, package, test, and release ExamCell as a standalone desktop application for both Linux and Windows.

The standalone editions allow institutions to use ExamCell without installing Python, PostgreSQL, or any additional dependencies.

---

# Supported Platforms

| Platform | Status     |
| -------- | ---------- |
| Linux    | Supported  |
| Windows  | Supported  |
| macOS    | Not Tested |

---

# Standalone Architecture

## Linux

User
→ launcher
→ Django
→ SQLite
→ runtime_data/
→ media/

## Windows

User
→ launcher.exe
→ Django
→ SQLite
→ runtime_data/
→ media/

---

# Build Requirements

## Development Dependencies

- Python 3.13+
- PyInstaller
- Django
- ReportLab
- OpenPyXL
- Pandas

Install:

```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

---

# Linux Build Process

## Step 1

Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 2

Clean Previous Builds

```bash
rm -rf build dist
```

## Step 3

Build Executable

```bash
pyinstaller -y launcher.spec
```

## Step 4

Verify Build Output

```bash
dist/
└── launcher/
    ├── launcher
    └── _internal/
```

---

# Windows Build Process

## Step 1

Open Git Bash

## Step 2

Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

## Step 3

Build Executable

```bash
pyinstaller -y launcher.spec
```

## Step 4

Verify Build Output

```text
dist/
└── launcher/
    ├── launcher.exe
    └── _internal/
```

---

# Runtime Data Architecture

ExamCell separates bundled application files from user-generated data.

## Runtime Folders

```text
runtime_data/
├── input/
└── output/

media/
```

Generated files are stored outside the application bundle.

---

# Database Strategy

## Development

PostgreSQL

## Cloud

PostgreSQL

## Standalone

SQLite

Database location:

```text
examcell.sqlite3
```

The database is automatically created during first launch.

---

# Startup Workflow

```text
launcher / launcher.exe
        │
        ▼
Environment Initialization
        │
        ▼
Runtime Folder Creation
        │
        ▼
SQLite Detection
        │
        ▼
Migration Execution
        │
        ▼
Django Startup
        │
        ▼
Browser Launch
```

---

# Static File Architecture

Static resources are bundled inside:

```text
_internal/static/
```

Contents:

```text
css/
js/
images/
samples/
```

Templates are bundled inside:

```text
_internal/templates/
```

---

# Migration Strategy

Every startup performs:

```bash
python manage.py migrate
```

Benefits:

- First-run initialization
- Automatic schema upgrades
- Version compatibility

---

# Testing Checklist

## Authentication

- Login
- Signup
- Logout

## Student Management

- CSV Upload
- Validation
- Upload History

## Exam Management

- Create Exam
- Edit Exam

## Hall Management

- Create Hall
- Capacity Calculation

## Seating Allocation

- Generate Allocation
- View Allocation

## Reporting

- PDF Export
- Excel Export

---

# Archive Testing

Before publishing a release:

## Linux

```bash
tar -czf ExamCell-Linux.tar.gz launcher/
```

Extract into a different folder and test.

## Windows

```text
Compress launcher/
to ZIP archive
```

Extract into a different folder and test.

---

# Release Packaging

## Linux Release

```text
Release/
└── ExamCell-Linux-vX.X.X/
```

Archive:

```text
ExamCell-Linux-vX.X.X.tar.gz
```

## Windows Release

```text
Release/
└── ExamCell-Windows-vX.X.X/
```

Archive:

```text
ExamCell-Windows-vX.X.X.zip
```

---

# GitHub Release Workflow

## Create Tag

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Publish Release

1. Open GitHub Releases
2. Create New Release
3. Select Tag
4. Upload Linux Archive
5. Upload Windows Archive
6. Publish

---

# Known Issues

## Windows

- First startup may be slightly slower than Linux.
- Windows Defender may scan executable files during launch.

## Linux

- Ensure executable permission exists.

```bash
chmod +x launcher
```

---

# Conclusion

ExamCell provides a fully portable standalone deployment solution for Linux and Windows. The architecture supports automatic database initialization, runtime data persistence, offline operation, and cross-platform distribution using PyInstaller.
