# System Architecture

## 1. Introduction

The ExamCell system follows a layered architecture based on the Django web framework. The architecture separates presentation, business logic, data processing, and database operations into independent modules, improving maintainability, scalability, and reliability.

The system is designed to support both web-based deployment and standalone desktop deployment using PyInstaller.

---

## 2. Architectural Overview

ExamCell follows the following architecture:

```text
+----------------------+
|      User Interface  |
| (HTML, CSS, JS)      |
+----------+-----------+
           |
           v
+----------------------+
|     Django Views     |
|     Request Layer    |
+----------+-----------+
           |
           v
+----------------------+
| Business Logic Layer |
|  Services & Rules    |
+----------+-----------+
           |
           v
+----------------------+
|      Data Layer      |
| Django ORM & Models  |
+----------+-----------+
           |
           v
+----------------------+
|      Database        |
| SQLite/PostgreSQL    |
+----------------------+
```

---

## 3. Application Modules

The system is divided into multiple Django applications.

### Accounts Module

Responsible for:

* User registration
* User authentication
* Login management
* Session handling
* Access control

---

### Students Module

Responsible for:

* Student data management
* CSV upload processing
* Data validation
* Upload history tracking
* Student record storage

---

### Exams Module

Responsible for:

* Examination creation
* Subject configuration
* Session management
* Examination scheduling information

---

### Halls Module

Responsible for:

* Hall creation
* Capacity management
* Bench configuration
* Hall availability management

---

### Seating Module

Responsible for:

* Seating allocation algorithm
* Student distribution
* Constraint validation
* Seating generation
* Seating visualization
* PDF export
* Excel export

This module represents the core functionality of the system.

---

### Dashboard Module

Responsible for:

* System statistics
* Activity monitoring
* Administrative overview
* Summary reports

---

## 4. Request Processing Flow

When a user performs an action, the system follows the sequence below:

```text
User
  |
  v
Browser
  |
  v
Django URL Router
  |
  v
View Function
  |
  v
Business Logic
  |
  v
Database Operation
  |
  v
Response Generation
  |
  v
Browser
```

---

## 5. Seating Generation Workflow

The seating arrangement generation process follows several stages.

### Step 1: Student Upload

* Student records are uploaded through CSV files.
* Data validation is performed.
* Invalid records are rejected.

### Step 2: Exam Configuration

* Examination details are created.
* Subject information is stored.

### Step 3: Hall Configuration

* Examination halls are configured.
* Hall capacities are defined.

### Step 4: Data Normalization

* Student data is cleaned.
* Records are sorted and prepared.

### Step 5: Allocation Processing

* Students are allocated to halls.
* Capacity constraints are applied.
* Allocation rules are enforced.

### Step 6: Report Generation

* Seating plans are generated.
* PDF reports are produced.
* Excel reports are produced.

---

## 6. Standalone Deployment Architecture

ExamCell supports standalone desktop deployment.

### Linux Deployment

```text
Launcher
    |
    v
Django Application
    |
    v
SQLite Database
    |
    v
Runtime Data Storage
```

### Windows Deployment

```text
launcher.exe
       |
       v
Django Application
       |
       v
SQLite Database
       |
       v
Runtime Data Storage
```

The standalone version automatically:

* Creates runtime directories
* Initializes SQLite databases
* Applies database migrations
* Serves static resources
* Opens the application in the default browser

---

## 7. Data Storage Architecture

The system uses separate locations for application resources and runtime data.

### Application Resources

```text
_static
_templates
_application files
```

### Runtime Data

```text
examcell.sqlite3
media/
runtime_data/
```

This separation ensures user-generated data remains persistent between application updates.

---

## 8. Security Architecture

The system includes:

* Authentication-based access control
* Session management
* Password hashing
* CSRF protection
* Input validation
* File validation mechanisms

---

## 9. Scalability Considerations

The architecture supports:

* SQLite for standalone deployment
* PostgreSQL for production deployment
* Cloud hosting environments
* Local desktop environments

This design allows the system to operate efficiently across different deployment models.

---

## 10. Conclusion

The modular architecture of ExamCell provides a maintainable, scalable, and reliable platform for examination hall seating arrangement automation. The separation of concerns between presentation, business logic, and data management improves system organization and future extensibility.
