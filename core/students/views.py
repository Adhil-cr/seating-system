from django.shortcuts import render

# Create your views here.

import os
import re
import pandas as pd
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError
from dashboard.models import ActivityLog
from .models import Student, Subject, UploadHistory, StorageArtifact
from seating.algorithms.csv_normalizer import normalize_and_sort_df, normalize_and_sort_csv
from utils.b2_storage import b2_enabled, build_prefix, timestamp_prefix, upload_bytes, upload_file, upload_fileobj


def _normalize_header(value):
    return re.sub(r"\s+", "", str(value).strip().lower())


def _find_column(columns, candidates):
    normalized = {_normalize_header(col): col for col in columns}
    for candidate in candidates:
        key = _normalize_header(candidate)
        if key in normalized:
            return normalized[key]
    return None


def _prepare_csv_for_normalizer(path):
    df = pd.read_csv(path)
    return _prepare_csv_for_normalizer_df(df)


def _prepare_csv_for_normalizer_df(df):
    if any(_normalize_header(col) == "#" for col in df.columns):
        raise ValueError(
            "Invalid CSV format: remove the leading '#' column "
            "and use the sample template headers."
        )

    reg_col = _find_column(
        df.columns,
        ["register no", "register_no", "reg no", "reg_no", "regno", "register number"]
    )
    name_col = _find_column(
        df.columns,
        ["student name", "student_name", "name"]
    )
    dept_col = _find_column(
        df.columns,
        ["branch", "department", "dept"]
    )
    sem_col = _find_column(
        df.columns,
        ["semester", "sem", "semister"]
    )

    missing = []
    if not reg_col:
        missing.append("Register No")
    if not name_col:
        missing.append("Student Name")
    if not dept_col:
        missing.append("Branch")
    if not sem_col:
        missing.append("Semester")
    if missing:
        raise ValueError(
            "Invalid CSV format. Missing columns: "
            f"{', '.join(missing)}. Use the sample template headers."
        )

    renames = {
        reg_col: "Register No",
        name_col: "Student Name",
    }
    if dept_col:
        renames[dept_col] = "Branch"
    if sem_col:
        renames[sem_col] = "Semester"

    df.rename(columns=renames, inplace=True)

    subject_cols = [
        col for col in df.columns
        if _normalize_header(col).startswith("sub")
    ]

    if not subject_cols:
        subject_col = _find_column(
            df.columns,
            ["subject_code", "subject codes", "subject", "subjects", "subject_codes"]
        )
        if not subject_col:
            raise ValueError(
                "Missing subject columns. Provide Sub1/Sub2... or subject_code."
            )

        subject_lists = []
        for value in df[subject_col].fillna(""):
            codes = [
                s.strip().replace(".0", "")
                for s in str(value).split(",")
                if s.strip()
            ]
            subject_lists.append(codes)

        max_len = max((len(items) for items in subject_lists), default=0)
        if max_len == 0:
            raise ValueError("No subject codes found in CSV.")

        for idx in range(max_len):
            col_name = f"Sub{idx + 1}"
            df[col_name] = [
                items[idx] if idx < len(items) else ""
                for items in subject_lists
            ]

        df.drop(columns=[subject_col], inplace=True)

    return df

    df = pd.read_csv(path)

    if any(_normalize_header(col) == "#" for col in df.columns):
        raise ValueError(
            "Invalid CSV format: remove the leading '#' column "
            "and use the sample template headers."
        )

    reg_col = _find_column(
        df.columns,
        ["register no", "register_no", "reg no", "reg_no", "regno", "register number"]
    )
    name_col = _find_column(
        df.columns,
        ["student name", "student_name", "name"]
    )
    dept_col = _find_column(
        df.columns,
        ["branch", "department", "dept"]
    )
    sem_col = _find_column(
        df.columns,
        ["semester", "sem", "semister"]
    )

    missing = []
    if not reg_col:
        missing.append("Register No")
    if not name_col:
        missing.append("Student Name")
    if not dept_col:
        missing.append("Branch")
    if not sem_col:
        missing.append("Semester")
    if missing:
        raise ValueError(
            "Invalid CSV format. Missing columns: "
            f"{', '.join(missing)}. Use the sample template headers."
        )

    renames = {
        reg_col: "Register No",
        name_col: "Student Name",
    }
    if dept_col:
        renames[dept_col] = "Branch"
    if sem_col:
        renames[sem_col] = "Semester"

    df.rename(columns=renames, inplace=True)

    subject_cols = [
        col for col in df.columns
        if _normalize_header(col).startswith("sub")
    ]

    if not subject_cols:
        subject_col = _find_column(
            df.columns,
            ["subject_code", "subject codes", "subject", "subjects", "subject_codes"]
        )
        if not subject_col:
            raise ValueError(
                "Missing subject columns. Provide Sub1/Sub2... or subject_code."
            )

        subject_lists = []
        for value in df[subject_col].fillna(""):
            codes = [
                s.strip().replace(".0", "")
                for s in str(value).split(",")
                if s.strip()
            ]
            subject_lists.append(codes)

        max_len = max((len(items) for items in subject_lists), default=0)
        if max_len == 0:
            raise ValueError("No subject codes found in CSV.")

        for idx in range(max_len):
            col_name = f"Sub{idx + 1}"
            df[col_name] = [
                items[idx] if idx < len(items) else ""
                for items in subject_lists
            ]

        df.drop(columns=[subject_col], inplace=True)

    df.to_csv(path, index=False)


@login_required
def upload_students(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file"}, status=400)

    media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
    filename = os.path.basename(file.name)

    try:
        file_bytes = file.read()
        if not file_bytes:
            return JsonResponse({"error": "Empty file"}, status=400)
        first_line = file_bytes.splitlines()[0].decode("utf-8", errors="ignore") if file_bytes else ""
        if ";" in first_line and "," not in first_line:
            return JsonResponse({
                "error": "Invalid CSV format: file appears semicolon-separated. Please save as a comma-separated CSV using the sample template."
            }, status=400)

        df_raw = pd.read_csv(pd.io.common.BytesIO(file_bytes))
        df_prepped = _prepare_csv_for_normalizer_df(df_raw)
        df = normalize_and_sort_df(df_prepped)
    except (ValueError, FileNotFoundError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"error": f"Upload failed: {exc}"}, status=500)

    required_cols = {"register_no", "student_name", "department", "semester", "subject_code"}
    if not required_cols.issubset(df.columns):
        return JsonResponse({"error": "Normalized CSV missing required columns."}, status=400)

    df["register_no"] = df["register_no"].astype(str).str.strip()
    df["student_name"] = df["student_name"].astype(str).str.strip()
    df["department"] = df["department"].astype(str).str.strip()
    df["subject_code"] = df["subject_code"].astype(str).str.strip().str.replace(".0", "", regex=False)

    df = df[df["register_no"].ne("") & df["student_name"].ne("") & df["department"].ne("")]
    df = df[df["subject_code"].ne("")]

    with transaction.atomic():
        Student.subjects.through.objects.filter(
            student__user=request.user
        ).delete()
        Student.objects.filter(user=request.user).delete()

        subjects_cache = {}

        for register_no, group in df.groupby("register_no", sort=False):
            name = group["student_name"].iloc[0]
            department = group["department"].iloc[0]
            semester_raw = group["semester"].dropna().iloc[0] if not group["semester"].dropna().empty else None

            semester = None
            if semester_raw not in (None, ""):
                try:
                    semester = int(float(str(semester_raw).strip()))
                except ValueError:
                    semester = None

            subject_codes = []
            for code in group["subject_code"].tolist():
                code_str = str(code).strip().replace(".0", "")
                if code_str and code_str not in subject_codes:
                    subject_codes.append(code_str)

            if not subject_codes:
                continue

            primary_subject_code = subject_codes[0][:20]

            student = Student.objects.create(
                user=request.user,
                register_no=register_no,
                name=name,
                department=department,
                semester=semester,
                subject_code=primary_subject_code
            )

            for code in subject_codes:
                subject = subjects_cache.get(code)
                if subject is None:
                    subject, _ = Subject.objects.get_or_create(code=code)
                    subjects_cache[code] = subject
                student.subjects.add(subject)

    total_students = Student.objects.filter(user=request.user).count()

    try:
        ActivityLog.objects.create(
            user=request.user,
            action=f"Uploaded students CSV: {total_students} students"
        )
    except (OperationalError, ProgrammingError):
        pass

    if b2_enabled():
        prefix = build_prefix('uploads', f'user_{request.user.id}', timestamp_prefix())
        original_key = build_prefix(prefix, filename)
        normalized_key = build_prefix(prefix, 'normalized_students.csv')

        if upload_bytes(file_bytes, original_key, content_type='text/csv'):
            StorageArtifact.objects.create(
                user=request.user,
                kind=StorageArtifact.KIND_UPLOAD_ORIGINAL,
                b2_key=original_key,
                file_name=filename
            )
        normalized_bytes = df.to_csv(index=False).encode('utf-8')
        if upload_bytes(normalized_bytes, normalized_key, content_type='text/csv'):
            StorageArtifact.objects.create(
                user=request.user,
                kind=StorageArtifact.KIND_UPLOAD_NORMALIZED,
                b2_key=normalized_key,
                file_name='normalized_students.csv'
            )

    UploadHistory.objects.create(
        user=request.user,
        file_name=filename,
        students_count=total_students
    )

    return JsonResponse({
        "message": "Students uploaded successfully",
        "total_students": total_students
    })


@login_required
def upload_history(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    uploads = UploadHistory.objects.filter(user=request.user).order_by("-uploaded_at")[:20]
    data = []
    for upload in uploads:
        data.append({
            "file_name": upload.file_name,
            "students_count": upload.students_count,
            "uploaded_at": upload.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "uploaded_by": request.user.get_full_name() or request.user.username
        })
    return JsonResponse(data, safe=False)
