import io
from django.test import TestCase, Client
from django.urls import reverse
from .models import EmployeeReport, StaffContact
from django.utils import timezone
from openpyxl import Workbook
from .models import EmployeeReport
from .services import parse_duration, import_excel_reports
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from .models import EmployeeReport, StaffContact
from django.test import RequestFactory, TestCase
from django.http import HttpResponse
from .decorators import require_api_key
from django.conf import settings


class DecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Create a dummy view protected by the decorator
        @require_api_key
        def dummy_view(request):
            return HttpResponse("Success")

        self.view = dummy_view

    def test_require_api_key_valid(self):
        request = self.factory.get('/test/')
        request.headers = {"X-API-KEY": settings.BALE_BOT_API_KEY}

        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success")

    def test_require_api_key_invalid(self):
        request = self.factory.get('/test/')
        request.headers = {"X-API-KEY": "wrong-key"}

        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_require_api_key_missing(self):
        request = self.factory.get('/test/')
        # No header at all
        request.headers = {}

        response = self.view(request)
        self.assertEqual(response.status_code, 403)


class ModelConstraintTests(TestCase):
    def test_unique_national_id(self):
        """Ensure national_id is unique across both models if intended,
           but specifically test StaffContact uniqueness here."""
        StaffContact.objects.create(
            national_id="123",
            phone_number="09121111111")
        with self.assertRaises(IntegrityError):
            StaffContact.objects.create(
                national_id="123", phone_number="09122222222")

    def test_leave_day_validator(self):
        """Ensure the PositiveSmallIntegerField validators work."""
        report = EmployeeReport(
            national_id="999",
            first_name="Test",
            last_name="User",
            annual_leave_days=35,  # Violates MaxValueValidator(31)
            total_shift_hours=10
        )
        # Note: Model validators are NOT automatically called on .save()
        # unless using a ModelForm. To test them manually:
        with self.assertRaises(ValidationError):
            report.full_clean()  # Triggers validation

    def test_staff_contact_index(self):
        """Verify the index exists on the model."""
        index_names = [index.name for index in StaffContact._meta.indexes]
        # Django automatically names indexes, verify the fields are in the Meta
        self.assertTrue(any(
            set(idx.fields) == {'national_id', 'phone_number'}
            for idx in StaffContact._meta.indexes
        ))


class ReportAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_key = settings.BALE_BOT_API_KEY
        # We assume settings.API_KEY is defined or matched in your decorator
        # Adjust the header key name if it differs from 'HTTP_X_API_KEY'
        self.headers = {"HTTP_X_API_KEY": self.api_key}

        # Create test data
        self.contact = StaffContact.objects.create(
            national_id="1234567890",
            phone_number="09120000000"
        )
        self.report = EmployeeReport.objects.create(
            national_id="1234567890",
            first_name="John",
            last_name="Doe",
            total_shift_hours=40,
            updated_at=timezone.now()
        )

    def test_validate_user_success(self):
        response = self.client.get(
            reverse('validate_user'),
            {'nid': '1234567890', 'phone': '09120000000'},
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'authorized')

    def test_validate_user_unauthorized(self):
        response = self.client.get(
            reverse('validate_user'),
            {'nid': '0000000000', 'phone': '0000000000'},
            **self.headers
        )
        self.assertEqual(response.status_code, 401)

    def test_get_report_success(self):
        response = self.client.get(
            reverse('get_report', kwargs={'national_id': '1234567890'}),
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['first_name'], 'John')

    def test_get_report_not_found(self):
        response = self.client.get(
            reverse('get_report', kwargs={'national_id': '999'}),
            **self.headers
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_api_key(self):
        # Test that request fails without the header
        response = self.client.get(reverse('validate_user'))
        self.assertEqual(response.status_code, 403)


class ServiceTests(TestCase):
    def test_parse_duration_valid(self):
        self.assertEqual(parse_duration("05:30"), {'hours': 5, 'minutes': 30})
        self.assertEqual(parse_duration("00:00"), {'hours': 0, 'minutes': 0})

    def test_parse_duration_invalid(self):
        self.assertEqual(
            parse_duration("invalid"), {
                'hours': -1, 'minutes': -1})
        self.assertEqual(
            parse_duration("25:61"), {
                'hours': -1, 'minutes': -1})  # Invalid range
        self.assertEqual(
            parse_duration("10:"), {
                'hours': -1, 'minutes': -1})    # Incomplete
        self.assertEqual(parse_duration(None), {'hours': -1, 'minutes': -1})

    def test_import_excel_reports(self):
        # 1. Create a dummy Excel file in memory
        wb = Workbook()
        ws = wb.active
        # Header row
        ws.append(["Row",
                   "Last",
                   "First",
                   "NID",
                   "Pres",
                   "Red",
                   "HLeave",
                   "HMiss",
                   "ALeave",
                   "SLeave",
                   "DMiss",
                   "Over",
                   "Shift"])
        # Data row
        ws.append([1, "Doe", "John", "1234567890", "08:00",
                  "01:00", "00:00", "00:00", 0, 0, 0, "02:00", 40])

        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # 2. Run the import
        count = import_excel_reports(excel_file)

        # 3. Verify
        self.assertEqual(count, 1)
        self.assertTrue(
            EmployeeReport.objects.filter(
                national_id="1234567890").exists())
        report = EmployeeReport.objects.get(national_id="1234567890")
        self.assertEqual(report.first_name, "John")
        self.assertEqual(report.total_presence, "08:00")
