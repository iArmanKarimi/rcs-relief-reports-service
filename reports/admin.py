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

@admin.register(StaffContact)
class StaffContactAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'phone_number')
    search_fields = ('national_id', 'phone_number')
