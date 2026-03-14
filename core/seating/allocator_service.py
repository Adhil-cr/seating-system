import os
import pandas as pd

from django.conf import settings

from .algorithms.csv_normalizer import normalize_and_sort_csv
from .algorithms.exam_session_preparer import prepare_exam_session
from .algorithms.seating_allocator import allocate_seating

from exams.models import Exam
from halls.models import Hall
from students.models import Student


def run_full_allocation_pipeline(exam, halls=None):

    base_dir = settings.BASE_DIR

    input_dir = os.path.join(base_dir, "runtime_data/input")
    output_dir = os.path.join(base_dir, "runtime_data/output")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    input_csv = os.path.join(input_dir, "raw_students.csv")
    normalized_csv = os.path.join(output_dir, "normalized.csv")

    # --------------------------------
    # STEP 1: Export students from DB
    # --------------------------------
    subject_codes = list(getattr(exam, "subject_codes", []) or [])
    if not subject_codes:
        subject_codes = list(
            exam.subjects.values_list("code", flat=True)
        )
    subject_codes = [str(code).strip().replace(".0", "") for code in subject_codes if str(code).strip()]

    if not subject_codes:
        raise ValueError("No subject codes configured for this exam.")

    students_qs = Student.objects.filter(
        user=exam.user,
        subjects__code__in=subject_codes
    ).distinct().prefetch_related("subjects")

    rows = []
    max_subjects = 0

    for student in students_qs:
        student_codes = list(
            student.subjects.filter(code__in=subject_codes)
            .values_list("code", flat=True)
        )
        if not student_codes and student.subject_code:
            raw_codes = [
                s.strip().replace(".0", "")
                for s in str(student.subject_code).split(",")
                if s.strip()
            ]
            student_codes = [code for code in raw_codes if code in subject_codes]
        if not student_codes:
            continue

        max_subjects = max(max_subjects, len(student_codes))
        rows.append({
            "Register No": student.register_no,
            "Student Name": student.name,
            "Branch": student.department,
            "Semester": student.semester if student.semester is not None else 1,
            "subjects": student_codes
        })

    if not rows:
        raise ValueError("No students found for selected subject codes.")

    data_rows = []
    for row in rows:
        record = {
            "Register No": row["Register No"],
            "Student Name": row["Student Name"],
            "Branch": row["Branch"],
            "Semester": row["Semester"]
        }
        for idx in range(max_subjects):
            key = f"Sub{idx + 1}"
            record[key] = row["subjects"][idx] if idx < len(row["subjects"]) else ""
        data_rows.append(record)

    df = pd.DataFrame(data_rows)
    df.to_csv(input_csv, index=False)

    # --------------------------------
    # STEP 2: Normalize CSV
    # --------------------------------

    normalize_and_sort_csv(
        input_file_path=input_csv,
        output_file_path=normalized_csv
    )

    # --------------------------------
    # STEP 3: Prepare Exam Session
    # --------------------------------

    if halls is None:
        halls = Hall.objects.filter(user=exam.user)
    else:
        if hasattr(halls, "all"):
            halls = halls.all()
        else:
            hall_ids = [h.id for h in halls]
            halls = Hall.objects.filter(id__in=hall_ids, user=exam.user)

    if halls.count() == 0:
        raise ValueError("No halls available for allocation.")

    exam_config = {
        "exam_date": str(exam.date),
        "session": exam.session,
        "subject_codes": subject_codes,
        "number_of_halls": halls.count(),
        "hall_capacity": halls.first().capacity,
        "invigilators_per_hall": 2
    }

    prepared_csv = prepare_exam_session(
        normalized_csv_path=normalized_csv,
        output_dir=output_dir,
        exam_config=exam_config
    )

    # --------------------------------
    # STEP 4: Run Seating Allocator
    # --------------------------------

    seating_config = {
        "number_of_halls": halls.count(),
        "hall_capacity": halls.first().capacity,
        "max_subject_per_hall": 12
    }

    result_csv = allocate_seating(
        prepared_csv_path=prepared_csv,
        output_dir=output_dir,
        seating_config=seating_config
    )

    return result_csv
