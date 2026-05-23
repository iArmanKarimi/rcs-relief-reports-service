import openpyxl
from .models import EmployeeReport


def parse_duration(hhmm: str):
    """
    Parses a "HH:mm" string into a dictionary/object with hours and minutes.
    Follows the strict domain convention:
    - Returns { 'hours': -1, 'minutes': -1 } for missing or invalid formats.
    - Handles '00:00' as { 'hours': 0, 'minutes': 0 }.
    """
    fallback = {'hours': -1, 'minutes': -1}

    if not hhmm or not isinstance(hhmm, str):
        return fallback

    parts = hhmm.strip().split(":")

    # Ensure exactly two parts
    if len(parts) != 2:
        return fallback

    # Check for empty strings in parts (e.g., "10:" or ":30")
    h_str, m_str = parts[0].strip(), parts[1].strip()
    if not h_str or not m_str:
        return fallback

    try:
        h = int(h_str)
        m = int(m_str)
    except ValueError:
        # One of the parts was not a valid number
        return fallback

    # Validate ranges
    if h < 0 or m < 0 or m > 59:
        return fallback

    return {'hours': h, 'minutes': m}


def import_excel_reports(file_path):
    """
    Parses the Excel file with maximum efficiency:
    - read_only=True: Streams the file, skipping heavy style parsing.
    - data_only=True: Reads calculated formula values instead of raw formulas.
    - with statement: Safely destroys and closes the workbook stream on exit.
    """

    # The context manager ensures everything is closed and garbage-collected
    # correctly.
    with openpyxl.load_workbook(file_path, read_only=True, data_only=True) as wb:
        sheet = wb.active

        # 1. Wipe existing data
        EmployeeReport.objects.all().delete()

        reports_to_create = []

        # 2. Generator-based streaming iteration
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Guard against empty/malformed rows
            if not row or len(row) < 13:
                continue

            # Excel columns map to 0-indexed tuple:
            # 0: Row Num, 1: Last Name, 2: First Name, 3: National ID, ...
            national_id = str(row[3]).strip() if row[3] is not None else None
            if not national_id:
                continue

            reports_to_create.append(
                EmployeeReport(
                    last_name=str(row[1] or ""),
                    first_name=str(row[2] or ""),
                    national_id=national_id,
                    total_presence=str(row[4] or "00:00"),
                    reduction_work=str(row[5] or "00:00"),
                    hourly_leave=str(row[6] or "00:00"),
                    hourly_mission=str(row[7] or "00:00"),
                    annual_leave_days=int(row[8] or 0),
                    sick_leave_days=int(row[9] or 0),
                    daily_mission_days=int(row[10] or 0),
                    total_overtime=str(row[11] or "00:00"),
                    total_shift_hours=int(row[12] or 0),
                )
            )

        # 3. Save to database in a single transaction block
        if reports_to_create:
            EmployeeReport.objects.bulk_create(reports_to_create)

        return len(reports_to_create)
