# reports/admin.py
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.urls import path
from django.shortcuts import redirect, render
from unfold.admin import ModelAdmin
from .models import EmployeeReport
from .excel import import_excel_reports
import tempfile
import os

admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(EmployeeReport)
class EmployeeReportAdmin(ModelAdmin):
    # Point to the custom template that contains the button
    change_list_template = "admin/employee_report_change_list.html"

    def has_add_permission(self, request, obj=None):
        return False

    def get_urls(self):
        # Register the custom URL for the import view
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
            
            # Save to temporary storage
            fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(fd)
            with open(tmp_path, "wb+") as dest:
                for chunk in excel_file.chunks():
                    dest.write(chunk)

            try:
                # Trigger your custom logic
                import_excel_reports(tmp_path)
                messages.success(request, "فایل با موفقیت بارگذاری و پردازش شد.")
            except Exception as e:
                messages.error(request, f"خطا در پردازش فایل: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            return redirect("admin:reports_employeereport_changelist")

        return render(request, "admin/import_excel.html", self.admin_site.each_context(request))
