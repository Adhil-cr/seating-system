import os
import pandas as pd
from datetime import datetime


def prepare_exam_session(
    normalized_csv_path: str,
    output_dir: str,
    exam_config: dict
) -> str:
    """
    Prepare a session-specific, constraint-ready dataset
    from normalized exam registrations.

    Args:
        normalized_csv_path (str): Path to normalized CSV
        output_dir (str): Directory to save prepared dataset
        exam_config (dict): Exam configuration parameters

    Returns:
        str: Path to generated prepared CSV
    """

    # ----------------------------
    # Step 1: Load normalized data
    # ----------------------------
    df = pd.read_csv(normalized_csv_path)

    required_cols = {
        "register_no",
        "student_name",
        "department",
        "semester",
        "subject_code"
    }

    if not required_cols.issubset(df.columns):
        raise ValueError("Normalized CSV schema mismatch.")

    # ----------------------------
    # Step 2: Read configuration
    # ----------------------------
    exam_date = exam_config["exam_date"]
    session = exam_config["session"]
    subject_codes = set(exam_config["subject_codes"])

    number_of_halls = exam_config["number_of_halls"]
    hall_capacity = exam_config["hall_capacity"]

    # ----------------------------
    # Step 3: Filter by subjects
    # ----------------------------
    session_df = df[df["subject_code"].isin(subject_codes)].copy()

    missing_subjects = subject_codes - set(session_df["subject_code"].unique())

    if missing_subjects:
        raise ValueError(
            f"Configured subject codes missing in prepared session: {missing_subjects}"
        )


    if session_df.empty:
        raise ValueError("No students found for selected subject codes.")

    # ----------------------------
    # Step 4: Capacity validation
    # ----------------------------
    total_students = len(session_df)
    total_capacity = number_of_halls * hall_capacity

    if total_students > total_capacity:
        raise ValueError(
            f"Capacity exceeded: {total_students} students "
            f"but only {total_capacity} seats available."
        )

    # ----------------------------
    # Step 5: Add session metadata
    # ----------------------------
    session_df["exam_date"] = exam_date
    session_df["session"] = session

    # ----------------------------
    # Step 6: Sort for predictability
    # ----------------------------
    session_df.sort_values(
        by=["subject_code", "department", "register_no"],
        inplace=True
    )

    # ----------------------------
    # Step 7: Export prepared CSV
    # ----------------------------
    os.makedirs(output_dir, exist_ok=True)

    filename = (
        f"prepared_exam_session_"
        f"{exam_date}_{session}.csv"
    )

    output_path = os.path.join(output_dir, filename)

    session_df.to_csv(output_path, index=False)

    return output_path


# ----------------------------
# CLI / Test Execution
# ----------------------------
if __name__ == "__main__":

    NORMALIZED_CSV = (
        "/home/adhil-cr/Desktop/Seating arrangment/"
        "seating_system/output_data/"
        "normalized_sorted_exam_registrations.csv"
    )

    OUTPUT_DIR = (
        "/home/adhil-cr/Desktop/Seating arrangment/"
        "seating_system/output_data"
    )

    exam_config = {
        "exam_date": "2026-03-10",
        "session": "FN",
        "subject_codes": [
            "2032",
            "2022",
            "4012",
            "4036",
            "6028",
            "6002",
        ],
        "number_of_halls": 40,
        "hall_capacity": 30,
        "invigilators_per_hall": 2
    }

    result = prepare_exam_session(
        normalized_csv_path=NORMALIZED_CSV,
        output_dir=OUTPUT_DIR,
        exam_config=exam_config
    )

    print("Prepared exam session dataset created at:")
    print(result)
