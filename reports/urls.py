from django.urls import path
from .views import validate_user, get_report

urlpatterns = [
    path("auth/validate/", validate_user, name="validate_user"),
    path("reports/<str:national_id>/", get_report, name="get_report"),
]
