from django.contrib import admin
from django.contrib.auth.models import Group, User
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import EmployeeReport, StaffContact

admin.site.unregister(User)
admin.site.unregister(Group)

class EmployeeReportResource(resources.ModelResource):
    class Meta:
        model = EmployeeReport
        # Exclude 'id' and 'updated_at' to prevent conflicts during import
        exclude = ('id', 'updated_at')
        # Ensure it maps correctly to your unique national_id
        import_id_fields = ('national_id',)
        # Skips rows that have no changes compared to the database
        skip_unchanged = True

class StaffContactResource(resources.ModelResource):
    class Meta:
        model = StaffContact
        # If you want to control import/export columns explicitly, uncomment:
        # fields = ("national_id", "phone_number")
        # import_id_fields = ("national_id",)
        
@admin.register(EmployeeReport)
class EmployeeReportAdmin(ImportExportModelAdmin):
    resource_class = EmployeeReportResource
    
    list_display = (
        'first_name', 
        'last_name', 
        'national_id', 
        'total_shift_hours', 
        'updated_at'
    )
    search_fields = ('first_name', 'last_name', 'national_id')
    
    class Meta:
        verbose_name = "گزارش کارمند"
        verbose_name_plural = "گزارش‌های کارمندان"
        
@admin.register(StaffContact)
class StaffContactAdmin(admin.ModelAdmin):
    resource_class = StaffContactResource
    
    list_display = ('national_id', 'phone_number')
    search_fields = ('national_id', 'phone_number')
