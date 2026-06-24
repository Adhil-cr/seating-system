# Release Notes

# ExamCell Release History

## Overview

This document records the actual release history of ExamCell based on the Git repository tags and published releases.

---

# Release Timeline

## v1.0-rc1 (Release Candidate 1)

### Summary

First Linux standalone release candidate used for validation and stabilization.

### Changes

- Refined standalone deployment configuration
- Applied fixes discovered during release candidate testing
- Improved CSV normalization behavior
- Improved standalone execution workflow
- Stabilized Linux standalone packaging

### Status

Superseded by RC2

---

## v1.0-rc2 (Release Candidate 2)

### Summary

Static file and media serving fix release.

### Major Fix

Resolved standalone deployment issues where:

- CSS files failed to load
- JavaScript files failed to load
- Images failed to load

### Changes

- Added standalone static URL routing
- Added standalone media URL routing
- Restored CSS loading
- Restored JavaScript loading
- Restored image loading
- Improved standalone deployment architecture

### Status

Release candidate completed successfully

---

## v1.0.0 (Stable Release)

### Summary

First stable production-ready ExamCell release.

### Release Name

ExamCell Linux v1.0.0

### Features Included

#### Authentication

- User registration
- User login
- Session management

#### Student Management

- CSV upload
- Student records
- Upload history

#### Examination Management

- Exam creation
- Subject configuration
- Session management

#### Hall Management

- Hall configuration
- Capacity calculation

#### Seating Allocation

- Automated seating generation
- Seating allocation storage
- Allocation viewing

#### Reports

- PDF export
- Excel export

#### Cloud Deployment

- Render hosting
- PostgreSQL database
- Backblaze B2 integration

#### Linux Standalone

- Portable executable
- SQLite database
- Runtime data persistence

#### Windows Standalone

Although the release tag was created during the Linux release cycle, the codebase was later validated successfully on Windows using:

- launcher.exe
- SQLite
- PyInstaller packaging
- Runtime data persistence

### Validation Results

Successfully tested:

- Signup
- Login
- CSV Upload
- Exam Creation
- Hall Creation
- Seating Generation
- PDF Export
- Excel Export

### Status

Stable

---

# Major Technical Milestones

## Seating Allocation Engine

Implemented:

- csv_normalizer.py
- validators.py
- exam_session_preparer.py
- seating_allocator.py
- allocator_service.py

---

## Cloud Deployment

Implemented:

- Render deployment
- PostgreSQL integration
- WhiteNoise
- Backblaze B2 storage

---

## Runtime Data Architecture

Introduced:

```text
runtime_data/
├── input/
└── output/

media/
```

Benefits:

- Persistent user files
- Portable standalone deployments
- Cleaner separation between bundled assets and generated data

---

## Cross Platform Support

| Platform | Status     |
| -------- | ---------- |
| Linux    | Supported  |
| Windows  | Supported  |
| macOS    | Not Tested |

---

# Important Deployment Fixes

## Static File Loading Fix

Problem:

Standalone builds could not load:

- CSS
- JavaScript
- Images

Solution:

- Explicit deployment modes
- Standalone static routes
- Standalone media routes
- Bundle/runtime separation

Result:

Fully functional standalone deployments.

---

## Runtime Persistence Fix

Problem:

Need to preserve user-generated files outside bundled application assets.

Solution:

- Dedicated runtime_data directory
- Dedicated media directory
- SQLite database beside executable

Result:

User data persists between launches.

---

# Current Stable State

The current codebase supports:

- Cloud deployment
- Linux standalone deployment
- Windows standalone deployment
- PostgreSQL
- SQLite
- PDF export
- Excel export
- Automated seating allocation

---

# Future Releases

Planned improvements:

- Role Based Access Control
- Multi Institution Support
- REST API
- Mobile Application
- Advanced Reporting
- AI Assisted Allocation Optimization

---

# Conclusion

ExamCell evolved from an academic project into a production-ready examination seating automation platform. The current stable release lineage consists of RC1, RC2, and the stable v1.0.0 release, with successful validation on both Linux and Windows standalone environments.
