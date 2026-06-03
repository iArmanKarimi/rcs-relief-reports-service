from django.http import JsonResponse
from .models import EmployeeReport, StaffContact
from .decorators import require_api_key


@require_api_key
def validate_user(request):
    phone = request.GET.get('phone')

    unauthorizedResponse = JsonResponse({"status": "unauthorized"}, status=401)

    if not phone:
        return unauthorizedResponse

    if len(phone) != 11:
        return unauthorizedResponse

    # Check if a contact record exists matching both
    is_valid = StaffContact.objects.filter(phone_number=phone).exists()

    if is_valid:
        return JsonResponse({"status": "authorized"}, status=200)
    return unauthorizedResponse


@require_api_key
def get_report_by_phone(request):
    phone = request.GET.get('phone')
    if not phone or len(phone) != 11:
        return JsonResponse({"error": "شماره تلفن نامعتبر است"}, status=400)

    try:
        contact = StaffContact.objects.get(phone_number=phone)
        national_id = getattr(contact, 'national_id', None)

        if not national_id:
            return JsonResponse({"error": "کد ملی برای این شماره تلفن یافت نشد"}, status=404)

        report = EmployeeReport.objects.get(national_id=national_id)

        data = {
            "national_id": report.national_id,
            "first_name": report.first_name,
            "last_name": report.last_name,
            "total_presence": report.total_presence,
            "reduction_work": report.reduction_work,
            "hourly_leave": report.hourly_leave,
            "hourly_mission": report.hourly_mission,
            "total_overtime": report.total_overtime,
            "annual_leave_days": report.annual_leave_days,
            "sick_leave_days": report.sick_leave_days,
            "daily_mission_days": report.daily_mission_days,
            "total_shift_hours": report.total_shift_hours,
            "updated_at": report.updated_at.isoformat(),
        }
        return JsonResponse(data)
    
    except StaffContact.DoesNotExist:
        return JsonResponse({"error": "شماره همراه در سیستم ثبت نشده است"}, status=404)

    except EmployeeReport.DoesNotExist:
        return JsonResponse({"error": "Report not found"}, status=404)
