# Database Design

## Overview

ExamCell uses a relational database architecture to manage users,
students, examinations, halls, seating allocations, uploads,
and activity logs.

The database is designed using normalization principles to
reduce redundancy and maintain data integrity.

---

## Entity Relationship Diagram

![ER Diagram](diagrams/database_er_diagram.png)

---

## Core Tables

### accounts_user

Stores application users.

| Field | Type | Description |
|---------|---------|---------|
| id | BigAutoField | Primary Key |
| username | CharField | Login username |
| email | EmailField | User email |
| role | CharField | Admin role |

---

### students_student

Stores student records.

| Field | Type | Description |
|---------|---------|---------|
| id | BigAutoField | Primary Key |
| register_no | CharField | Register number |
| name | CharField | Student name |
| department | CharField | Branch |
| semester | IntegerField | Semester |

---

### students_subject

Stores subject codes.

| Field | Type |
|---------|---------|
| id | BigAutoField |
| code | CharField |

---

### exams_exam

Stores examination configurations.

| Field | Type |
|---------|---------|
| id | BigAutoField |
| name | CharField |
| date | DateField |
| session | CharField |

---

### halls_hall

Stores examination halls.

| Field | Type |
|---------|---------|
| id | BigAutoField |
| name | CharField |
| rows | IntegerField |
| columns | IntegerField |
| seats_per_bench | IntegerField |

---

### seating_seatingallocation

Stores generated allocation sessions.

| Field | Type |
|---------|---------|
| id | BigAutoField |
| exam_id | ForeignKey |
| created_at | DateTimeField |

---

### seating_seat

Stores individual seat assignments.

| Field | Type |
|---------|---------|
| id | BigAutoField |
| allocation_id | ForeignKey |
| hall_id | ForeignKey |
| student_id | ForeignKey |
| row | IntegerField |
| column | IntegerField |

---

### students_uploadhistory

Tracks uploaded CSV files.

### students_storageartifact

Tracks generated files and runtime outputs.

### dashboard_activitylog

Stores user activity records.

---

## Relationships

### User Relationships

- One User can create many Exams.
- One User can create many Halls.
- One User can upload many Student files.

### Student Relationships

- One Student can have multiple Subjects.
- One Subject can belong to multiple Students.

### Exam Relationships

- One Exam can contain multiple Subjects.
- One Exam can generate multiple Seating Allocations.

### Hall Relationships

- One Hall contains multiple Seats.

### Seating Relationships

- One Seating Allocation contains many Seat records.

---

## Database Integrity Constraints

- Register number uniqueness per user.
- Subject code uniqueness.
- Foreign key constraints.
- Cascade deletion policies.
- Data validation through Django ORM.

---

## Summary

The database architecture provides a scalable and normalized
structure for managing examination seating allocation,
student records, hall configurations, and generated reports.
