# Feature Documentation

## Overview

ExamCell is a web-based examination seating arrangement automation system developed using Django and PostgreSQL/SQLite.

The system automates student data management, examination configuration, hall management, seating allocation, and report generation.

---

# Feature Modules

1. User Management
2. Student Management
3. Examination Management
4. Hall Management
5. Seating Allocation Engine
6. Report Generation
7. Dashboard & Analytics
8. File Management

1. User Management
### Purpose

Provides secure access to the system.

### Features

- User Registration
- User Login
- User Logout
- Session Management
- Role-based access

### Benefits

- Secure authentication
- User-specific data isolation
- Activity tracking


2. Student Management
### Purpose

Manage student records through CSV uploads.

### Features

- Bulk Student Upload
- CSV Validation
- Duplicate Detection
- Subject Extraction
- Semester Detection
- Department Mapping

### Workflow

CSV Upload
→ Validation
→ Normalization
→ Database Storage

### Outputs

- Student Records
- Subject Records
- Upload History


3. Examination Management
### Purpose

Create and manage examination sessions.

### Features

- Exam Creation
- Date Selection
- Session Selection (AM/PM)
- Subject Selection
- Subject Code Mapping

### Benefits

- Organized exam scheduling
- Multi-subject support


4. Hall Management
### Purpose

Configure examination halls.

### Features

- Hall Creation
- Row Configuration
- Column Configuration
- Bench Capacity Configuration
- Hall Activation / Deactivation

### Capacity Calculation

Hall Capacity =
Rows × Columns × Seats Per Bench

### Benefits

- Flexible hall configuration
- Dynamic capacity calculation


5. Seating Allocation Engine
### Purpose

Automatically generate seating arrangements.

### Features

- Subject-wise allocation
- Hall distribution
- Seat assignment
- Conflict avoidance
- Capacity validation

### Workflow

Students
→ Exam Selection
→ Hall Selection
→ Allocation Engine
→ Seat Assignment

### Rules

- Hall capacity must not be exceeded.
- Students should be distributed fairly.
- Allocation data is stored for future viewing.

### Outputs

- Seating Allocation
- Seat Records


6. Report Generation
### Purpose

Generate downloadable reports.

### Features

- PDF Export
- Excel Export
- Hall-wise Reports
- Allocation Reports

### Technologies

- ReportLab
- OpenPyXL

### Benefits

- Printable reports
- Easy distribution


7. Dashboard & Analytics
### Purpose

Provide system statistics.

### Features

- Student Count
- Exam Count
- Hall Count
- Seating Allocation Count

### Benefits

- Quick system overview
- Operational visibility


8. File Management
### Purpose

Track uploaded and generated files.

### Features

- Upload History
- Storage Artifacts
- Runtime Outputs
- Generated Reports Tracking

### Stored Files

- Uploaded CSV
- Normalized CSV
- Generated Excel
- Generated PDF


## Technical Highlights

### Backend

- Python
- Django

### Database

- PostgreSQL
- SQLite

### Frontend

- HTML
- CSS
- JavaScript

### Reporting

- ReportLab
- OpenPyXL

### Deployment

- Render Cloud
- Standalone Executable

### Build Tools

- PyInstaller


## Summary

ExamCell provides a complete examination seating management solution by automating student processing, examination scheduling, hall management, seating allocation, and report generation.

The modular architecture allows deployment both as a cloud-hosted web application and as a standalone executable for offline institutional use.
