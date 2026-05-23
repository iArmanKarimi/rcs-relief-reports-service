from django.contrib import admin
from import_export import resources
from import_export.admin import ImportMixin
from .models import EmployeeReport


class EmployeeReportResource(resources.ModelResource):
    """Define the Resource for import/export logic"""
    class Meta:
        model = EmployeeReport
        # Exclude 'id' and 'updated_at' to prevent conflicts during import
        exclude = ('id', 'updated_at')
        # Ensure it maps correctly to your unique national_id
        import_id_fields = ('national_id',)
        # Set to True if you want it to skip records that don't change
        skip_unchanged = True


@admin.register(EmployeeReport)
class EmployeeReportAdmin(ImportMixin, admin.ModelAdmin):
    '''Register the Admin with ImportMixin'''
    resource_class = EmployeeReportResource

    list_display = (
        'first_name', 'last_name', 'national_id',
        'total_shift_hours', 'updated_at'
    )
    search_fields = ('first_name', 'last_name', 'national_id')
