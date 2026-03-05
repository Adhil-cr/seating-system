import os
import pandas as pd

from django.conf import settings

from .algorithms.csv_normalizer import normalize_and_sort_csv
from .algorithms.exam_session_preparer import prepare_exam_session
from .algorithms.seating_allocator import allocate_seating

from exams.models import Exam
from halls.models import Hall
from students.models import Student


def run_full_allocation_pipeline(exam):

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

    students = Student.objects.all().values(
        "register_no",
        "name",
        "department"
    )

    df = pd.DataFrame(list(students))

    df.rename(columns={
        "name": "Student Name",
        "register_no": "Register No",
        "department": "Branch"
    }, inplace=True)

    df["Semester"] = 1
    df["Sub1"] = "GEN"

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

    halls = Hall.objects.all()

    exam_config = {
        "exam_date": str(exam.date),
        "session": "FN",
        "subject_codes": list(
            exam.subjects.values_list("code", flat=True)
        ),
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