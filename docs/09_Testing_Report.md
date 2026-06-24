# Testing Report

# ExamCell Testing Report

## Introduction

This document summarizes the testing activities performed for ExamCell across development, cloud deployment, Linux standalone deployment, and Windows standalone deployment.

The objective was to verify system functionality, stability, portability, and correctness.

---

# Testing Environment

## Development Environment

| Component | Value |
|------------|------------|
| OS | Fedora Linux |
| Python | 3.13 |
| Framework | Django 4.2.11 |
| Database | PostgreSQL |

---

## Linux Standalone Environment

| Component | Value |
|------------|------------|
| OS | Fedora Linux |
| Packaging | PyInstaller |
| Database | SQLite |
| Runtime | launcher |

---

## Windows Standalone Environment

| Component | Value |
|------------|------------|
| OS | Windows 11 |
| Packaging | PyInstaller |
| Database | SQLite |
| Runtime | launcher.exe |

---

# Functional Testing

## Authentication Module

| Test Case | Expected Result | Status |
|------------|----------------|---------|
| User Signup | Account created successfully | PASS |
| User Login | User redirected to dashboard | PASS |
| Invalid Login | Error returned | PASS |
| Session Handling | Session maintained correctly | PASS |

---

## Student Management Module

| Test Case | Expected Result | Status |
|------------|----------------|---------|
| CSV Upload | File uploaded successfully | PASS |
| CSV Validation | Invalid records detected | PASS |
| Upload History | Records displayed | PASS |
| Student Storage | Records saved correctly | PASS |

---

## Examination Module

| Test Case | Expected Result | Status |
|------------|----------------|---------|
| Create Exam | Exam created | PASS |
| Subject Mapping | Subjects assigned correctly | PASS |
| Exam Retrieval | Exam displayed correctly | PASS |

---

## Hall Management Module

| Test Case | Expected Result | Status |
|------------|----------------|---------|
| Create Hall | Hall saved | PASS |
| Capacity Calculation | Capacity generated correctly | PASS |
| Hall Listing | Hall displayed | PASS |

---

## Seating Allocation Module

| Test Case | Expected Result | Status |
|------------|----------------|---------|
| Generate Allocation | Allocation generated | PASS |
| Hall Assignment | Students assigned correctly | PASS |
| Capacity Validation | Capacity rules enforced | PASS |
| Allocation Storage | Allocation stored | PASS |

---

## Report Generation

| Test Case | Expected Result | Status |
|------------|----------------|---------|
| PDF Export | PDF generated | PASS |
| Excel Export | Excel generated | PASS |
| Report Download | Download successful | PASS |

---

# Integration Testing

| Integration | Status |
|-------------|---------|
| Students ↔ Exams | PASS |
| Exams ↔ Halls | PASS |
| Halls ↔ Seating Engine | PASS |
| Seating Engine ↔ Reports | PASS |
| Dashboard ↔ Database | PASS |

---

# Linux Standalone Testing

## Build Validation

| Test | Status |
|--------|---------|
| PyInstaller Build | PASS |
| Launcher Startup | PASS |
| SQLite Initialization | PASS |
| Migration Execution | PASS |
| Static Files Loading | PASS |
| Template Loading | PASS |

---

## Functional Validation

| Test | Status |
|--------|---------|
| Signup | PASS |
| Login | PASS |
| CSV Upload | PASS |
| Hall Creation | PASS |
| Exam Creation | PASS |
| Seating Generation | PASS |
| PDF Export | PASS |
| Excel Export | PASS |

---

## Archive Relocation Testing

Procedure:

1. Create release archive.
2. Extract into a different folder.
3. Launch application.
4. Verify functionality.

Result:

PASS

---

# Windows Standalone Testing

## Build Validation

| Test | Status |
|--------|---------|
| PyInstaller Build | PASS |
| launcher.exe Startup | PASS |
| SQLite Initialization | PASS |
| Migration Execution | PASS |
| Static Files Loading | PASS |
| Template Loading | PASS |

---

## Functional Validation

| Test | Status |
|--------|---------|
| Signup | PASS |
| Login | PASS |
| CSV Upload | PASS |
| Hall Creation | PASS |
| Exam Creation | PASS |
| Seating Generation | PASS |
| PDF Export | PASS |
| Excel Export | PASS |

---

# Cloud Deployment Testing

| Test | Status |
|--------|---------|
| Application Deployment | PASS |
| PostgreSQL Connection | PASS |
| Backblaze B2 Storage | PASS |
| Static File Delivery | PASS |
| Authentication | PASS |
| Seating Allocation | PASS |
| PDF Export | PASS |
| Excel Export | PASS |

---

# Static File Verification

Verified Resources:

```text
static/css/main.css
static/js/app.js
static/js/dashboard.js
static/images/benchmap_logo.png
```

Result:

PASS

---

# Database Verification

## PostgreSQL

- CRUD Operations
- Authentication Storage
- Student Records
- Exam Records
- Hall Records

Result:

PASS

---

## SQLite

- First Launch Initialization
- Migration Execution
- Data Persistence

Result:

PASS

---

# Performance Observations

## Linux

- Fast startup
- Responsive UI
- Minimal delay

## Windows

- Slightly slower startup
- Windows Defender scanning may affect launch time

Both platforms remained fully functional.

---

# Defects Identified and Resolved

## Static File Loading Failure

Issue:

Standalone build returned HTTP 404 for CSS, JS, and images.

Resolution:

- Introduced explicit deployment modes.
- Added standalone static routes.
- Implemented bundle/runtime separation.
- Updated launcher initialization process.

Status:

RESOLVED

---

## Runtime Data Persistence

Issue:

Need for persistent user-generated files outside bundled application assets.

Resolution:

- Introduced runtime_data directory.
- Added input/output separation.
- Stored generated files outside application bundle.

Status:

RESOLVED

---

# Final Test Summary

| Category | Status |
|-----------|---------|
| Authentication | PASS |
| Students | PASS |
| Exams | PASS |
| Halls | PASS |
| Seating | PASS |
| Reports | PASS |
| Linux Standalone | PASS |
| Windows Standalone | PASS |
| Cloud Deployment | PASS |

---

# Conclusion

Testing confirmed that ExamCell operates correctly across development, cloud-hosted, Linux standalone, and Windows standalone environments. All critical features were validated successfully, and identified deployment issues were resolved before release.
