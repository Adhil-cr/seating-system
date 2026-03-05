print("PYTHON FILE LOADED")

"""
Module: csv_normalizer.py

Purpose:
- Normalize exam registration CSV
- Convert multi-subject columns into single-subject rows
- Sort by subject code
"""

import os
import pandas as pd
from data_processing.validators import validate_normalized_csv


def normalize_and_sort_csv(input_file_path: str, output_file_path: str) -> None:
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Input file not found: {input_file_path}")

    print("Reading CSV file...")

    # Your CSV is already clean and comma-separated
    df = pd.read_csv(input_file_path)

    print("Available columns:", list(df.columns))

    # Required columns (EXACT names)
    REQUIRED_COLUMNS = [
        "Register No",
        "Student Name",
        "Branch",
        "Semester"
    ]

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    print("Detecting subject columns...")

    subject_columns = [c for c in df.columns if c.startswith("Sub")]

    if not subject_columns:
        raise ValueError("No subject columns found (Sub1, Sub2, ...).")

    print(f"Found subject columns: {subject_columns}")

    print("Normalizing data (one row per student per subject)...")

    normalized_rows = []

    for _, row in df.iterrows():
        for sub_col in subject_columns:
            subject_code = row[sub_col]

            if pd.notna(subject_code) and str(subject_code).strip():
                normalized_rows.append({
                    "register_no": row["Register No"],
                    "student_name": row["Student Name"],
                    "department": row["Branch"],
                    "semester": int(row["Semester"]),
                    "subject_code": str(subject_code).strip().replace(".0", "")
                })

    if not normalized_rows:
        raise ValueError("No valid subject registrations found.")

    normalized_df = pd.DataFrame(normalized_rows)

    # FIX: enforce subject_code as string identifier
    normalized_df["subject_code"] = normalized_df["subject_code"].astype(str).str.strip()

    validate_normalized_csv(normalized_df)

    print("Sorting by subject code...")

    normalized_df.sort_values(
        by="subject_code",
        inplace=True
    )

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    normalized_df.to_csv(output_file_path, index=False)

    print("✅ Normalization and sorting completed successfully.")
    print(f"Output saved to: {output_file_path}")


#  ---------------- ENTRY POINT ----------------

if __name__ == "__main__":
    print("MAIN BLOCK EXECUTED")

    INPUT_FILE = "/home/adhil-cr/Desktop/Seating arrangment/seating_system/Input_data/StudentExamCenterCourses (7).csv"
    OUTPUT_FILE = "/home/adhil-cr/Desktop/Seating arrangment/seating_system/output_data/normalized_sorted_exam_registrations.csv"

    normalize_and_sort_csv(INPUT_FILE, OUTPUT_FILE)
