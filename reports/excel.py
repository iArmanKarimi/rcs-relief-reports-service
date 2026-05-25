# reports/excel.py
import openpyxl
from openpyxl import load_workbook
from .models import EmployeeReport, StaffContact
from django.db import transaction

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


def normalize_excel_value(value):
    """
    Convert Excel cell value to clean string.
    Handles ints/floats like 1234567890.0 -> '1234567890'
    Also handles None and string cleanup.
    """
    if value is None:
        return ""
    
    # If it's already an int
    if isinstance(value, int):
        return str(value)
    
    # If it's a float that is actually a whole number
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).strip()
    
    # Otherwise string cleanup
    text = str(value).strip()
    if text.endswith(".0"): # Remove trailing ".0" if it's a float represented as string
        text = text[:-2]
    return text


def import_excel_reports(file_path):
    """
    Parses the Excel file with maximum efficiency:
    - read_only=True: Streams the file, skipping heavy style parsing.
    - data_only=True: Reads calculated formula values instead of raw formulas.
    - with statement: Safely destroys and closes the workbook stream on exit.
    """
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    try:
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
            # 0: Row Num, 1: Last Name, 2: First Name, 3: National ID, 
            # 4: Total Presence, 5: Reduction Work, 6: Hourly Leave, 
            # 7: Hourly Mission, 8: Annual Leave Days, 9: Sick Leave Days, 
            # 10: Daily Mission Days, 11: Total Overtime, 12: Total Shift Hours
            
            national_id = normalize_excel_value(row[3])
            if not national_id or not national_id.isdigit() or len(national_id) != 10:
                continue # Skip if National ID is missing or not purely digits

            reports_to_create.append(
                EmployeeReport(
                    last_name=normalize_excel_value(row[1]),
                    first_name=normalize_excel_value(row[2]),
                    national_id=national_id,
                    total_presence=str(row[4] or "00:00"), # Keep as string for parse_duration later if needed
                    reduction_work=str(row[5] or "00:00"),
                    hourly_leave=str(row[6] or "00:00"),
                    hourly_mission=str(row[7] or "00:00"),
                    annual_leave_days=int(normalize_excel_value(row[8]) or 0),
                    sick_leave_days=int(normalize_excel_value(row[9]) or 0),
                    daily_mission_days=int(normalize_excel_value(row[10]) or 0),
                    total_overtime=str(row[11] or "00:00"),
                    total_shift_hours=int(normalize_excel_value(row[12]) or 0),
                )
            )

        # 3. Save to database in a single transaction block
        if reports_to_create:
            EmployeeReport.objects.bulk_create(reports_to_create)

        return len(reports_to_create)
    finally:
        wb.close()


def import_excel_contacts(file_path):
    wb = load_workbook(file_path, data_only=True)
    sheet = wb.active

    contacts_to_create = []
    skipped_rows = []

    # skip header
    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        nid = normalize_excel_value(row[0])
        phone = normalize_excel_value(row[1])

        # Validation: nid must be 10 digits, phone must be 11 digits
        if len(nid) == 10 and nid.isdigit() and len(phone) == 11 and phone.isdigit():
            contacts_to_create.append(
                StaffContact(national_id=nid, phone_number=phone)
            )
        else:
            # Track rows that don't meet the criteria
            skipped_rows.append(idx)

    if contacts_to_create:
        StaffContact.objects.bulk_create(contacts_to_create, ignore_conflicts=True)

    wb.close()
    return len(contacts_to_create), skipped_rows
