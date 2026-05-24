from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import EmployeeReport, StaffContact

# 1. Define the Resource for import/export logic
class EmployeeReportResource(resources.ModelResource):
    class Meta:
        model = EmployeeReport
        # Exclude 'id' and 'updated_at' to prevent conflicts during import
        exclude = ('id', 'updated_at')
        # Ensure it maps correctly to your unique national_id
        import_id_fields = ('national_id',)
        # Skips rows that have no changes compared to the database
        skip_unchanged = True

# 2. Register the EmployeeReport with ImportExportModelAdmin
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
    
    # Optional: Add your custom action back if you still need it
    actions = ['test_button']

    @admin.action(description="تست دکمه")
    def test_button(self, request, queryset):
        self.message_user(request, "دکمه‌ها کار می‌کنند!")

# 3. Register the StaffContact model
@admin.register(StaffContact)
class StaffContactAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'phone_number')
    search_fields = ('national_id', 'phone_number')
