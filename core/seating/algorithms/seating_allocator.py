import os
import pandas as pd
from collections import defaultdict, deque


# ============================================================
# Public Orchestrator
# ============================================================

def allocate_seating(
    prepared_csv_path: str,
    output_dir: str,
    seating_config: dict
) -> str:
    """
    Allocate seats to students based on hall capacity,
    subject distribution limits, and bench-based in-hall reordering
    (no same department on the same bench).

    Pipeline:
      1) Load prepared data
      2) Allocate students to halls (existing logic, preserved)
      3) Reorder seats within each hall by benches (NEW)
      4) Assign seat numbers and export CSV
    """

    # ----------------------------
    # Step 1: Load prepared data
    # ----------------------------
    df = pd.read_csv(prepared_csv_path)

    required_cols = {
        "register_no",
        "student_name",
        "department",
        "subject_code",
        "exam_date",
        "session"
    }
    if not required_cols.issubset(df.columns):
        raise ValueError("Prepared CSV schema mismatch.")

    # FIX: multi-subject student handling
    # Ensure expected columns exist for downstream logic.
    if "primary_subject" not in df.columns:
        df["primary_subject"] = df["subject_code"]
    if "is_multi_subject" not in df.columns:
        counts = df["register_no"].value_counts()
        df["is_multi_subject"] = df["register_no"].map(
            lambda reg: counts.get(reg, 0) > 1
        )

    # ----------------------------
    # Step 2: Read configuration
    # ----------------------------
    number_of_halls = seating_config["number_of_halls"]
    hall_capacity = seating_config["hall_capacity"]
    max_subject_per_hall = seating_config["max_subject_per_hall"]

    if hall_capacity % 2 != 0:
        raise ValueError("Hall capacity must be even (2 seats per bench).")

    # ----------------------------
    # Step 3: Allocate students to halls (UNCHANGED LOGIC)
    # ----------------------------
    # FIX: multi-subject student handling
    # Allocate a single physical seat per unique register_no, using primary_subject.
    unique_rows = []
    for reg, group in df.groupby("register_no", sort=False):
        student_name = group["student_name"].iloc[0]
        department = group["department"].iloc[0]
        primary_subject = str(group["primary_subject"].iloc[0]).strip()
        if not primary_subject:
            primary_subject = str(group["subject_code"].iloc[0]).strip()

        unique_rows.append({
            "register_no": reg,
            "student_name": student_name,
            "department": department,
            "subject_code": primary_subject
        })

    unique_df = pd.DataFrame(unique_rows)

    halls = _allocate_students_to_halls(
        df=unique_df,
        number_of_halls=number_of_halls,
        hall_capacity=hall_capacity,
        max_subject_per_hall=max_subject_per_hall
    )

    # ----------------------------
    # Step 4: Reorder seats within each hall by benches (NEW)
    # ----------------------------
    for hall in halls:
        hall["seats"] = _reorder_hall_seats_by_bench(hall["seats"])

    # ----------------------------
    # Step 5: Generate output rows with seat numbers
    # ----------------------------
    output_rows = _generate_output_rows(halls, df)

    output_df = pd.DataFrame(output_rows)

    # ----------------------------
    # Step 6: Export CSV
    # ----------------------------
    os.makedirs(output_dir, exist_ok=True)
    exam_date = df.iloc[0]["exam_date"]
    session = df.iloc[0]["session"]

    filename = f"seat_allocated_exam_session_{exam_date}_{session}.csv"
    output_path = os.path.join(output_dir, filename)
    output_df.to_csv(output_path, index=False)

    return output_path


# ============================================================
# Internal Helpers
# ============================================================

def _allocate_students_to_halls(
    df: pd.DataFrame,
    number_of_halls: int,
    hall_capacity: int,
    max_subject_per_hall: int
):
    """
    Existing hall allocation logic (preserved).
    Allocates students to halls respecting:
      - hall capacity
      - max students per subject per hall
      - soft department mixing at hall level
    """

    halls = []
    for hall_id in range(1, number_of_halls + 1):
        halls.append({
            "hall_id": hall_id,
            "capacity": hall_capacity,
            "occupied": 0,
            "subject_counts": defaultdict(int),
            "department_counts": defaultdict(int),
            "seats": []
        })

    # Group students by subject
    subject_groups = defaultdict(list)
    for _, row in df.iterrows():
        subject_groups[row["subject_code"]].append(row)

    # Sort subjects by descending size
    sorted_subjects = sorted(
        subject_groups.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    # Allocate
    for subject_code, students in sorted_subjects:
        for student in students:
            allocated = False

            halls_sorted = sorted(
                halls,
                key=lambda h: (
                    h["subject_counts"][subject_code],
                    h["department_counts"][student["department"]],
                    h["occupied"]
                )
            )

            for hall in halls_sorted:
                if hall["occupied"] >= hall["capacity"]:
                    continue
                if hall["subject_counts"][subject_code] >= max_subject_per_hall:
                    continue

                hall["seats"].append({
                    "register_no": student["register_no"],
                    "student_name": student["student_name"],
                    "department": student["department"],
                    "subject_code": subject_code
                })
                hall["occupied"] += 1
                hall["subject_counts"][subject_code] += 1
                hall["department_counts"][student["department"]] += 1

                allocated = True
                break

            if not allocated:
                raise ValueError(
                    f"Seating allocation failed for subject {subject_code}. "
                    f"Constraints too strict."
                )

    return halls


def _reorder_hall_seats_by_bench(seats):
    """
    Reorder seats so that no two students of the same department
    sit on the same bench (2 seats per bench).

    Best-effort strategy:
      - Pair students from different departments per bench
      - If only one department remains, fill sequentially
    """

    if not seats:
        return seats

    # Group seats by department into queues
    dept_queues = defaultdict(deque)
    for s in seats:
        dept_queues[s["department"]].append(s)

    # Sort departments by remaining count (descending)
    def sort_depts():
        return sorted(
            dept_queues.keys(),
            key=lambda d: len(dept_queues[d]),
            reverse=True
        )

    reordered = []

    while True:
        # Remove empty departments
        for d in list(dept_queues.keys()):
            if not dept_queues[d]:
                del dept_queues[d]

        if not dept_queues:
            break

        depts = sort_depts()

        # If at least two departments available, pair them
        if len(depts) >= 2:
            d1, d2 = depts[0], depts[1]
            reordered.append(dept_queues[d1].popleft())
            reordered.append(dept_queues[d2].popleft())
        else:
            # Only one department left: best-effort fill
            d = depts[0]
            reordered.append(dept_queues[d].popleft())
            if dept_queues[d]:
                reordered.append(dept_queues[d].popleft())
            else:
                break

    return reordered


def _generate_output_rows(halls, prepared_df):
    """
    Assign seat numbers sequentially per hall and then
    replicate the same hall_id/seat_number for all subject rows
    of the same register_no.
    """
    # FIX: multi-subject student handling
    # Build a seat assignment map per register_no.
    seat_map = {}
    for hall in halls:
        seat_number = 1
        for seat in hall["seats"]:
            seat_map[seat["register_no"]] = {
                "hall_id": hall["hall_id"],
                "seat_number": seat_number
            }
            seat_number += 1

    # FIX: multi-subject student handling
    # Precompute primary + arrear subjects per student.
    subject_map = {}
    primary_map = {}
    arrear_map = {}
    for reg, group in prepared_df.groupby("register_no", sort=False):
        codes = []
        for code in group["subject_code"].tolist():
            code_str = str(code).strip().replace(".0", "")
            if code_str and code_str not in codes:
                codes.append(code_str)

        primary_subject = ""
        if "primary_subject" in group.columns:
            primary_subject = str(group["primary_subject"].iloc[0]).strip()
        if not primary_subject and codes:
            primary_subject = codes[0]

        subject_map[reg] = codes
        primary_map[reg] = primary_subject
        arrear_map[reg] = ",".join([c for c in codes if c != primary_subject])

    rows = []
    for _, row in prepared_df.iterrows():
        reg = row["register_no"]
        assignment = seat_map.get(reg)
        if not assignment:
            raise ValueError(f"Seat assignment missing for register_no {reg}")

        rows.append({
            "register_no": row["register_no"],
            "student_name": row["student_name"],
            "department": row["department"],
            "subject_code": row["subject_code"],
            "primary_subject": primary_map.get(reg, ""),
            "arrear_subjects": arrear_map.get(reg, ""),
            "is_multi_subject": bool(row.get("is_multi_subject", False)),
            "hall_id": assignment["hall_id"],
            "seat_number": assignment["seat_number"]
        })

    return rows


# ============================================================
# CLI / Test Execution
# ============================================================

if __name__ == "__main__":

    PREPARED_CSV = (
        "/home/adhil-cr/Desktop/Seating arrangment/"
        "seating_system/output_data/"
        "prepared_exam_session_2026-03-10_FN.csv"
    )

    OUTPUT_DIR = (
        "/home/adhil-cr/Desktop/Seating arrangment/"
        "seating_system/output_data"
    )

    seating_config = {
        "number_of_halls": 26,
        "hall_capacity": 20,        # must be even
        "max_subject_per_hall": 12,
    }

    result = allocate_seating(
        prepared_csv_path=PREPARED_CSV,
        output_dir=OUTPUT_DIR,
        seating_config=seating_config
    )

    print("Seat allocation completed successfully:")
    print(result)
