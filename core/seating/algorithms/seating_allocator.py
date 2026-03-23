import os
import math
import logging
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

    # FIX: deduplicate multi-subject students
    # Ensure expected columns exist for downstream logic.
    if "is_multi_subject" not in df.columns:
        counts = df["register_no"].value_counts()
        df["is_multi_subject"] = df["register_no"].map(
            lambda reg: counts.get(reg, 0) > 1
        )

    # ----------------------------
    # Step 2: Read configuration
    # ----------------------------
    number_of_halls = seating_config["number_of_halls"]
    hall_capacity = seating_config.get("hall_capacity")
    hall_capacities = seating_config.get("hall_capacities")
    hall_bench_sizes = seating_config.get("hall_bench_sizes")
    hall_columns = seating_config.get("hall_columns")
    max_subject_per_hall = seating_config["max_subject_per_hall"]

    if hall_capacities:
        if len(hall_capacities) != number_of_halls:
            raise ValueError("Hall capacities count does not match number_of_halls.")
    if hall_bench_sizes:
        if len(hall_bench_sizes) != number_of_halls:
            raise ValueError("Hall bench sizes count does not match number_of_halls.")
    if hall_columns:
        if len(hall_columns) != number_of_halls:
            raise ValueError("Hall columns count does not match number_of_halls.")

    # ----------------------------
    # Step 3: Allocate students to halls (UNCHANGED LOGIC)
    # ----------------------------
    # FIX: deduplicate multi-subject students
    # Build a primary row per register_no using the lowest subject_code
    # and keep all subjects on that row for output expansion.
    unique_rows = []
    for reg, group in df.groupby("register_no", sort=False):
        student_name = group["student_name"].iloc[0]
        department = group["department"].iloc[0]

        subjects = []
        for code in group["subject_code"].tolist():
            code_str = str(code).strip().replace(".0", "")
            if code_str and code_str not in subjects:
                subjects.append(code_str)

        if not subjects:
            continue

        primary_subject = sorted(subjects)[0]

        unique_rows.append({
            "register_no": reg,
            "student_name": student_name,
            "department": department,
            "subject_code": primary_subject,
            "all_subjects": subjects,
            "is_multi_subject": len(subjects) > 1
        })

    unique_df = pd.DataFrame(unique_rows)

    # FIX: multi-subject student handling
    # Relax subject-per-hall constraint if it's too strict for actual subject counts.
    subject_counts = unique_df["subject_code"].value_counts()
    if not subject_counts.empty:
        min_required = max(
            math.ceil(count / number_of_halls)
            for count in subject_counts.values
        )
    else:
        min_required = 0
    effective_max_subject_per_hall = max(max_subject_per_hall, min_required)

    halls = _allocate_students_to_halls(
        df=unique_df,
        number_of_halls=number_of_halls,
        hall_capacity=hall_capacity,
        hall_capacities=hall_capacities,
        hall_bench_sizes=hall_bench_sizes,
        hall_columns=hall_columns,
        max_subject_per_hall=effective_max_subject_per_hall
    )

    # ----------------------------
    # Step 4: Reorder seats within each hall by benches (NEW)
    # ----------------------------
    for hall in halls:
        hall["seats"] = _reorder_hall_seats_by_bench(
            hall["seats"],
            bench_size=hall.get("bench_size", 2),
            columns=hall.get("columns")
        )

    # ----------------------------
    # Step 5: Generate output rows with seat numbers
    # ----------------------------
    output_rows = _generate_output_rows(halls)

    output_columns = [
        "register_no",
        "student_name",
        "department",
        "subject_code",
        "hall_id",
        "seat_number",
        "is_multi_subject"
    ]
    output_df = pd.DataFrame(output_rows, columns=output_columns)

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
    hall_capacities,
    hall_bench_sizes,
    hall_columns,
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
        capacity = hall_capacity
        if hall_capacities:
            capacity = hall_capacities[hall_id - 1]
        columns = None
        if hall_columns:
            columns = hall_columns[hall_id - 1]
        bench_size = 2
        if hall_bench_sizes:
            bench_size = int(hall_bench_sizes[hall_id - 1]) or 2
        if bench_size < 1:
            bench_size = 1
        halls.append({
            "hall_id": hall_id,
            "capacity": capacity,
            "columns": columns,
            "bench_size": bench_size,
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
                    "subject_code": subject_code,
                    "all_subjects": student.get("all_subjects", [subject_code]),
                    "is_multi_subject": student.get("is_multi_subject", False)
                })
                hall["occupied"] += 1
                hall["subject_counts"][subject_code] += 1
                hall["department_counts"][student["department"]] += 1

                allocated = True
                break

            if not allocated:
                # Best-effort fallback: if subject-per-hall limit is too strict,
                # place the student in any hall with remaining capacity.
                for hall in halls_sorted:
                    if hall["occupied"] >= hall["capacity"]:
                        continue

                    hall["seats"].append({
                        "register_no": student["register_no"],
                        "student_name": student["student_name"],
                        "department": student["department"],
                        "subject_code": subject_code,
                        "all_subjects": student.get("all_subjects", [subject_code]),
                        "is_multi_subject": student.get("is_multi_subject", False)
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


def _reorder_hall_seats_by_bench(seats, bench_size=2, columns=None):
    """
    Reorder seats so that no two students of the same department
    sit on the same bench (bench_size seats per bench).

    Best-effort strategy:
      - Pair students from different departments per bench
      - If only one department remains, fill sequentially
    """

    if not seats:
        return seats

    if bench_size < 1:
        bench_size = 1

    # Group seats by department into queues
    dept_queues = defaultdict(deque)
    for s in seats:
        dept_queues[s["department"]].append(s)

    if bench_size == 1:
        # Round-robin by department to avoid large departments dominating early seats.
        dept_order = sorted(
            dept_queues.keys(),
            key=lambda d: (-len(dept_queues[d]), d)
        )
        dept_cycle = deque(dept_order)
        ordered = []

        while dept_cycle:
            dept = dept_cycle.popleft()
            queue = dept_queues.get(dept)
            if not queue:
                continue
            ordered.append(queue.popleft())
            if queue:
                dept_cycle.append(dept)

        total_seats = len(ordered)
        if total_seats == 0:
            return ordered

        if columns is None or int(columns) < 1:
            columns = total_seats

        columns = int(columns)
        rows = total_seats // columns
        if total_seats % columns != 0:
            rows += 1
        rows = max(rows, 1)

        grid = [[None for _ in range(columns)] for _ in range(rows)]

        def _subjects(student):
            subjects = student.get("all_subjects") or [student.get("subject_code")]
            return {
                str(code).strip().replace(".0", "")
                for code in subjects
                if str(code).strip()
            }

        def _has_conflict(a, b):
            if not a or not b:
                return False
            if a.get("department") != b.get("department"):
                return False
            return bool(_subjects(a) & _subjects(b))

        def _is_safe(r, c, student):
            if c - 1 >= 0 and _has_conflict(student, grid[r][c - 1]):
                return False
            if r - 1 >= 0 and _has_conflict(student, grid[r - 1][c]):
                return False
            return True

        remaining = ordered[:]
        reordered = []
        logger = logging.getLogger(__name__)

        for r in range(rows):
            for c in range(columns):
                if not remaining:
                    break
                chosen_idx = None
                for idx, candidate in enumerate(remaining):
                    if _is_safe(r, c, candidate):
                        chosen_idx = idx
                        break
                if chosen_idx is None:
                    chosen_idx = 0
                    logger.warning(
                        "Adjacency constraint fallback in bench_size=1 hall placement."
                    )
                chosen = remaining.pop(chosen_idx)
                grid[r][c] = chosen
                reordered.append(chosen)

        return reordered

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

        # Build one bench with as much department diversity as possible
        bench = []
        for d in depts:
            if len(bench) >= bench_size:
                break
            if dept_queues.get(d):
                bench.append(dept_queues[d].popleft())

        # If bench not full, fill with remaining students (best-effort)
        if len(bench) < bench_size:
            for d in sort_depts():
                while len(bench) < bench_size and dept_queues.get(d):
                    bench.append(dept_queues[d].popleft())
                if len(bench) >= bench_size:
                    break

        reordered.extend(bench)

    return reordered


def _generate_output_rows(halls):
    """
    Assign seat numbers sequentially per hall and then
    expand each allocated seat into one row per subject.
    """
    rows = []

    for hall in halls:
        seat_number = 1
        for seat in hall["seats"]:
            # FIX: output expansion for multi-subject students
            all_subjects = seat.get("all_subjects") or [seat["subject_code"]]
            is_multi = seat.get("is_multi_subject", len(all_subjects) > 1)

            for subject in all_subjects:
                rows.append({
                    "register_no": seat["register_no"],
                    "student_name": seat["student_name"],
                    "department": seat["department"],
                    "subject_code": subject,
                    "hall_id": hall["hall_id"],
                    "seat_number": seat_number,
                    "is_multi_subject": is_multi
                })

            seat_number += 1

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
