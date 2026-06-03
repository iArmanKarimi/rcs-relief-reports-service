from django.urls import path
from .views import validate_user, get_report_by_phone

urlpatterns = [
    path("auth/validate/", validate_user, name="validate_user"),
    path("reports/by-phone/", get_report_by_phone, name="get_report_by_phone"),
]
