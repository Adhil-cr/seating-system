import pandas as pd


def validate_normalized_csv(df: pd.DataFrame) -> None:
    """
    Validate normalized exam registration data.
    Raises ValueError if any validation fails.
    """

    # ----------------------------
    # 1. Required columns
    # ----------------------------
    required_cols = {
        "register_no",
        "student_name",
        "department",
        "semester",
        "subject_code",
    }

    if not required_cols.issubset(df.columns):
        raise ValueError("Normalized CSV missing required columns")

    # ----------------------------
    # 2. subject_code integrity
    # ----------------------------
    if df["subject_code"].isna().any():
        raise ValueError("Normalized data contains empty subject_code")

    if df["subject_code"].astype(str).str.strip().eq("").any():
        raise ValueError("Normalized data contains blank subject_code")

    if df["subject_code"].astype(str).str.contains(r"\.0$", regex=True).any():
        raise ValueError(
            "subject_code contains Excel-style '.0' values (data not canonicalized)"
        )

    # ----------------------------
    # 3. register_no integrity
    # ----------------------------
    if df["register_no"].isna().any():
        raise ValueError("Normalized data contains empty register_no")

    # ----------------------------
    # 4. Duplicate registration check
    # ----------------------------
    duplicates = df.duplicated(subset=["register_no", "subject_code"])
    if duplicates.any():
        raise ValueError(
            "Duplicate (register_no, subject_code) pairs found in normalized data"
        )
