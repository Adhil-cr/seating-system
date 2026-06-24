# Deployment Guide

# ExamCell Cloud Deployment Guide

## Introduction

This document describes the deployment architecture and production deployment process used by ExamCell.

ExamCell supports cloud hosting using Django, PostgreSQL, WhiteNoise, and Backblaze B2 object storage.

---

# Production Architecture

```text
Users
   │
   ▼
Web Browser
   │
   ▼
Render Web Service
   │
   ▼
Django Application
   │
   ├── PostgreSQL Database
   │
   └── Backblaze B2 Storage
```

---

# Deployment Platforms

| Component | Platform |
|------------|------------|
| Application Hosting | Render |
| Database | PostgreSQL |
| Object Storage | Backblaze B2 |
| Static Files | WhiteNoise |
| Source Control | GitHub |

---

# Technology Stack

## Backend

- Python
- Django

## Database

- PostgreSQL

## Storage

- Backblaze B2

## Static Files

- WhiteNoise

---

# Environment Variables

Required production variables:

```env
SECRET_KEY=your-secret-key

DEBUG=False

DATABASE_URL=postgresql://...

ALLOWED_HOSTS=your-domain.com

B2_STORAGE_ENABLED=True

B2_KEY_ID=xxxxx
B2_APP_KEY=xxxxx
B2_BUCKET=xxxxx
B2_ENDPOINT=xxxxx
B2_REGION=xxxxx
```

---

# PostgreSQL Configuration

ExamCell uses PostgreSQL in cloud deployments.

Database configuration is automatically loaded using:

```python
dj_database_url.parse()
```

Benefits:

- Reliability
- Scalability
- Production-grade storage
- Concurrent access support

---

# Backblaze B2 Storage

Purpose:

- Store uploaded files
- Store generated reports
- Offload media storage

Configuration:

```python
DEFAULT_FILE_STORAGE =
"storages.backends.s3boto3.S3Boto3Storage"
```

Benefits:

- Lower storage cost
- Cloud accessibility
- Durable storage

---

# WhiteNoise Configuration

Purpose:

Serve static files directly from Django.

Configuration:

```python
STATICFILES_STORAGE =
"whitenoise.storage.CompressedManifestStaticFilesStorage"
```

Benefits:

- No separate CDN required
- Compressed assets
- Faster page loading

---

# Render Deployment Process

## Step 1

Push code to GitHub.

```bash
git push origin master
```

---

## Step 2

Create Render Web Service.

Settings:

```text
Environment:
Python

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn core.wsgi
```

---

## Step 3

Create PostgreSQL Database

Provision PostgreSQL from Render.

Copy:

```text
DATABASE_URL
```

Add it to environment variables.

---

## Step 4

Configure Environment Variables

Add all required production variables.

---

## Step 5

Deploy Application

Render automatically:

- Builds project
- Installs dependencies
- Runs application

---

# Static Files Deployment

Collect static files:

```bash
python manage.py collectstatic
```

Generated location:

```text
staticfiles/
```

Served by:

```text
WhiteNoise
```

---

# Security Configuration

## Enabled Features

- CSRF Protection
- Session Security
- Password Hashing
- ORM Query Protection
- Input Validation

---

# Deployment Validation Checklist

## Authentication

- Login
- Signup

## Students

- CSV Upload
- Upload History

## Exams

- Create Exam
- View Exam

## Halls

- Create Hall
- Edit Hall

## Seating

- Generate Allocation
- View Allocation

## Reports

- PDF Export
- Excel Export

---

# Monitoring

Verify:

- Application availability
- Database connectivity
- Storage availability
- Error logs
- Performance metrics

---

# Backup Strategy

## Database

Regular PostgreSQL backups.

## Storage

Backblaze B2 redundancy.

## Source Code

GitHub repository.

---

# Maintenance

Regularly:

- Update dependencies
- Review logs
- Test exports
- Verify backups
- Monitor database usage

---

# Troubleshooting

## Static Files Not Loading

Verify:

```bash
collectstatic
```

and WhiteNoise configuration.

---

## Database Connection Error

Verify:

```text
DATABASE_URL
```

configuration.

---

## Storage Upload Error

Verify:

```text
B2 credentials
Bucket name
Endpoint URL
```

---

# Conclusion

ExamCell's cloud deployment architecture provides a scalable, secure, and maintainable solution for educational institutions. By combining Django, PostgreSQL, WhiteNoise, and Backblaze B2, the system supports reliable examination management and seating allocation in production environments.
