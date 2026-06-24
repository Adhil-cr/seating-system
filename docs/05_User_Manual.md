# User Manual

## Introduction

ExamCell is an Examination Seating Arrangement Automation System developed to simplify and automate the process of generating examination seating plans.

The system allows administrators to upload student data, configure examinations and halls, generate seating arrangements, and export reports.

---

## System Requirements

### Minimum Requirements

- Windows 10/11 or Linux
- 4 GB RAM
- 500 MB Free Storage
- Modern Web Browser

### Recommended

- 8 GB RAM
- Google Chrome / Microsoft Edge



## 1. Login

![01-login.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/01-login.png)

### Purpose

Allows authorized users to access the system.

### Steps

1. Open ExamCell.
2. Enter Username.
3. Enter Password.
4. Click Login.

### Result

User is redirected to Dashboard.



## 2. User Registration

![02-signup.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/02-signup.png)

### Purpose

Create a new administrator account.

### Steps

1. Open Signup Page.
2. Enter User Details.
3. Create Username.
4. Create Password.
5. Submit Form.

### Result

New account is created successfully.



## 3. Dashboard

![03-dashboard.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/03-dashboard.png)

### Purpose

Provides a quick overview of the system.

### Available Information

- Total Students
- Total Exams
- Total Halls
- Total Allocations

### Benefits

Allows administrators to monitor system status.





## 4. Upload Student Data

![04-student-upload.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/04-student-upload.png)

### Purpose

Import student records from CSV.

### Steps

1. Open Student Upload page.
2. Select CSV File.
3. Click Upload.
4. Wait for validation.

### Result

Students are added to the database.



# CSV Format Section

### Supported CSV Format

| Register No | Student Name | Branch | Semester | Sub1   |
| ----------- | ------------ | ------ | -------- | ------ |
| CE001       | John         | CE     | 5        | CST301 |





## 5. Create Examination

![05-exam-config.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/05-exam-config.png)

### Steps

1. Open Exam Configuration.
2. Enter Exam Name.
3. Select Date.
4. Select Session.
5. Select Subject Codes.
6. Save Examination.





## 6. Configure Halls

![06-hall-config.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/06-hall-config.png)

### Steps

1. Open Hall Configuration.
2. Enter Hall Name.
3. Enter Rows.
4. Enter Columns.
5. Enter Seats Per Bench.
6. Save Hall.





## 7. Generate Seating Arrangement

![07-seating-generate.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/07-seating-generate.png)

### Steps

1. Open Seating Generation.
2. Select Examination.
3. Select Available Halls.
4. Click Generate.

### Result

System automatically generates seat allocation.





## 8. View Seating Arrangement

![08-seating-view.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/08-seating-view.png)

### Features

- Hall-wise View
- Student Allocation View
- Seat Information

### Benefits

Allows verification before examination.





## 9. Export Reports

![09-pdf-export.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/09-pdf-export.png)



![10-excel-export.png](/home/adhil-cr/Desktop/seating-system/docs/screenshots/10-excel-export.png)

### PDF Export

1. Open Seating View.
2. Click Export PDF.

Output:
Hall-wise seating report.

### Excel Export

1. Open Seating View.
2. Click Export Excel.

Output:
Spreadsheet containing seat allocations.



    

## Troubleshooting

### CSV Upload Failed

Cause:
Invalid CSV format.

Solution:
Verify column names.

---

### Seating Generation Failed

Cause:
Insufficient hall capacity.

Solution:
Add more halls or increase capacity.

---

### Login Failed

Cause:
Invalid credentials.

Solution:
Verify username and password.



## Best Practices

- Verify uploaded student records.
- Confirm hall capacities before allocation.
- Generate seating plans before exam day.
- Export PDF and Excel backups.



## Conclusion

ExamCell provides a simple and efficient workflow for examination seating management, reducing manual effort and improving allocation accuracy.
