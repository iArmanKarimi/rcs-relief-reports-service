from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class EmployeeReport(models.Model):
    national_id = models.CharField(
        "کد ملی", max_length=10, unique=True, db_index=True)
    first_name = models.CharField("نام", max_length=100)
    last_name = models.CharField("نام خانوادگی", max_length=100)

    # Time durations (hh:mm)
    total_presence = models.CharField("مجموع حضور", max_length=10)
    reduction_work = models.CharField("کسر کار", max_length=10)
    hourly_leave = models.CharField("مرخصی ساعتی", max_length=10)
    hourly_mission = models.CharField("ماموریت ساعتی", max_length=10)
    total_overtime = models.CharField("اضافه کار", max_length=10)

    # Numeric values (using corrected Validators and default)
    annual_leave_days = models.PositiveSmallIntegerField(
        "مرخصی استحقاقی (روز)",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(31)]
    )
    sick_leave_days = models.PositiveSmallIntegerField(
        "مرخصی استعلاجی (روز)",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(31)]
    )
    daily_mission_days = models.PositiveSmallIntegerField(
        "ماموریت روزانه (روز)",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(31)]
    )

    total_shift_hours = models.PositiveSmallIntegerField("مجموع ساعت شیفت")

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی", auto_now=True, editable=False)

    class Meta:
        verbose_name = "گزارش عملکرد پرسنل"
        verbose_name_plural = "گزارش‌ عملکرد پرسنل"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.national_id}"


class StaffContact(models.Model):
    national_id = models.CharField(
        "کد ملی", max_length=10, unique=True, db_index=True)
    phone_number = models.CharField("شماره موبایل", max_length=11, unique=True)

    class Meta:
        indexes = [models.Index(fields=['national_id', 'phone_number'])]
        verbose_name = "اطلاعات تماس "
        verbose_name_plural = "اطلاعات تماس پرسنل"

    def __str__(self):
        return f"(کد ملی) {self.national_id} - (شماره تماس) {self.phone_number}"