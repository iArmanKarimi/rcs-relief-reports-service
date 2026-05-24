# reports/admin.py
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.urls import path
from django.shortcuts import redirect, render
from unfold.admin import ModelAdmin
from .models import EmployeeReport, StaffContact
from .excel import import_excel_reports, import_excel_contacts
import tempfile
import os

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(EmployeeReport)
class EmployeeReportAdmin(ModelAdmin):
    change_list_template = "admin/employee_report_change_list.html"
    list_display = ("first_name", "last_name", "national_id")
    search_fields = ("first_name", "last_name", "national_id")

    def has_add_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel_view),
                name="reports_employeereport_import_excel",
            ),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        if request.method == "POST" and request.FILES.get("excel_file"):
            excel_file = request.FILES["excel_file"]

            fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(fd)
            with open(tmp_path, "wb+") as dest:
                for chunk in excel_file.chunks():
                    dest.write(chunk)

            try:
                import_excel_reports(tmp_path)
                messages.success(request, "گزارش‌ها با موفقیت بارگذاری و پردازش شدند.")
            except Exception as e:
                messages.error(request, f"خطا در پردازش فایل: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            return redirect("admin:reports_employeereport_changelist")

        return render(request, "admin/import_excel.html", self.admin_site.each_context(request))


@admin.register(StaffContact)
class StaffContactAdmin(ModelAdmin):
    change_list_template = "admin/staff_contact_change_list.html"

    # This splits the data into two columns
    list_display = ("national_id", "phone_number")
    search_fields = ("national_id", "phone_number")

    def has_add_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel_view),
                name="reports_staffcontact_import_excel",
            ),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        if request.method == "POST" and request.FILES.get("excel_file"):
            excel_file = request.FILES["excel_file"]

            fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(fd)
            with open(tmp_path, "wb+") as dest:
                for chunk in excel_file.chunks():
                    dest.write(chunk)

            try:
                created_count, skipped_rows = import_excel_contacts(tmp_path)
                
                msg = f"مخاطبین با موفقیت بارگذاری شدند. {created_count} ردیف ثبت شد."
                if skipped_rows:
                    msg += f" (ردیف‌های نادیده گرفته شده: {', '.join(map(str, skipped_rows))})"
                
                messages.success(request, msg)
            except Exception as e:
                messages.error(request, f"خطا در پردازش فایل: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            return redirect("admin:reports_staffcontact_changelist")

        return render(request, "admin/import_excel.html", self.admin_site.each_context(request))
