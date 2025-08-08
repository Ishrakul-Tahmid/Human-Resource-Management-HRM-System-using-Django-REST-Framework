from django.utils import timezone
from django.db import models
from employee.models import Employee
from leave_management.models import Supervisor
from django.dispatch import receiver
from django.db.models.signals import post_save
from employee.models import Employee, Department, Branch
from django.core.exceptions import ValidationError

# Create your models here.

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances', blank=True, null=True)
    rfid_no = models.CharField(max_length=20, blank=True, null=True)
    attendance_date = models.DateTimeField(blank=True, null=True)
    # in_time = models.TimeField(blank=True, null=True)
    # out_time = models.TimeField(blank=True, null=True)
    # late_by = models.DurationField(blank=True, null=True)
    # early_out_by = models.DurationField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
        ('half_day', 'Half Day'),
        ('late_in', 'Late In'),
        ('early_out', 'Early Out'),
    ], default='present')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


    class Meta:
        unique_together = ('employee', 'attendance_date')
        ordering = ['-attendance_date']
    
    def __str__(self):
        attendance_local_time = timezone.localtime(self.attendance_date) if self.attendance_date else None
        return f"{self.employee} - {attendance_local_time} - {self.status}"
    
class ShiftInOut(models.Model):
    """Tracks in and out times for employees"""
    name = models.CharField(max_length=100, blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift_in_outs', blank=True, null=True)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='shift_in_outs', blank=True, null=True)
    in_time = models.TimeField(blank=True, null=True)
    shifting_in_start = models.TimeField(default=timezone.datetime.strptime("08:00", "%H:%M").time(), blank=True, null=True)
    shifting_in_end = models.TimeField(default=timezone.datetime.strptime("11:00", "%H:%M").time() ,blank=True, null=True)
    out_time = models.TimeField(blank=True, null=True)
    shifting_out_start = models.TimeField(default=timezone.datetime.strptime("16:00", "%H:%M").time() , blank=True, null=True)
    shifting_out_end = models.TimeField(default=timezone.datetime.strptime("20:00", "%H:%M").time() , blank=True, null=True)
    consideration_time = models.DurationField(blank=True, null=True, default=timezone.timedelta(minutes=20), help_text="Time considered for attendance calculation")

    class Meta:
        unique_together = ('employee', 'attendance')
        ordering = ['-attendance__attendance_date']
    
    def __str__(self):
        locals_attendance_time = timezone.localtime(self.attendance.attendance_date) if self.attendance and self.attendance.attendance_date else None
        return f"{self.employee} - {locals_attendance_time} - In: {self.in_time} - Out: {self.out_time}"
    
@receiver(post_save, sender=Attendance)
def create_shift_in_out(sender, instance, created, **kwargs):
    if not created or not instance.employee or not instance.attendance_date:
        return

    attendance_date = instance.attendance_date.date()
    attendances = Attendance.objects.filter(
        employee=instance.employee,
        attendance_date__date=attendance_date
    ).order_by('attendance_date')

    # Use the default shift window values from ShiftInOut model
    default_in_start = ShiftInOut._meta.get_field('shifting_in_start').default
    default_in_end = ShiftInOut._meta.get_field('shifting_in_end').default
    default_out_start = ShiftInOut._meta.get_field('shifting_out_start').default
    default_out_end = ShiftInOut._meta.get_field('shifting_out_end').default

    # Find in-time attendance
    in_attendance = attendances.filter(
        attendance_date__time__gte=default_in_start,
        attendance_date__time__lte=default_in_end
    ).first()

    # Find out-time attendance
    out_attendance = attendances.filter(
        attendance_date__time__gte=default_out_start,
        attendance_date__time__lte=default_out_end
    ).last()

    # Only create if both in and out attendance exist
    if in_attendance and out_attendance:
        # Check if ShiftInOut already exists for this employee and date
        if not ShiftInOut.objects.filter(
            employee=instance.employee,
            attendance__attendance_date__date=attendance_date
        ).exists():
            shift_name = ""
            if(
                default_in_start == timezone.datetime.strptime("08:00", "%H:%M").time() and default_out_end == timezone.datetime.strptime("20:00", "%H:%M").time()
            ):
                shift_name = "Day Shift"
            elif(
                default_in_start == timezone.datetime.strptime("20:00", "%H:%M").time() and default_out_end == timezone.datetime.strptime("08:00", "%H:%M").time()):
                shift_name = "Night Shift"
            ShiftInOut.objects.create(
                name=shift_name,
                employee=instance.employee,
                attendance=in_attendance,  # You can also use out_attendance, as both are for the same date
                in_time=timezone.localtime(in_attendance.attendance_date).time(),
                out_time=timezone.localtime(out_attendance.attendance_date).time(),
            )
    
class AttendanceAdjustment(models.Model):
    ADJUSTMENT_TYPE = [
        ('forgot_sign_in', 'Forgot Sign In'),
        ('forgot_sign_out', 'Forgot Sign Out'),
        ('traffic_delay', 'Traffic Delay'),
        ('personal_emergency', 'Personal Emergency'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_adjustments', blank=True, null=True)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='attendance_adjustments', blank=True, null=True)
    adjustment_type = models.CharField(max_length=50, choices=ADJUSTMENT_TYPE, blank=True, null=True)
    timeframe_start = models.DateTimeField(blank=True, null=True)
    timeframe_end = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending_L1', 'Pending Level 1'),
        ('pending_L2', 'Pending Level 2'),
        ('pending_L3', 'Pending Level 3'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending_L1')
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'attendance', 'adjustment_type')
        ordering = ['-timeframe_start']
    
    def __str__(self):
        return f"{self.employee} - {self.adjustment_type} - ({self.status})"
    
class AdjustmentApproval(models.Model):
    adjustment_request = models.ForeignKey(
        AttendanceAdjustment, on_delete=models.CASCADE,
        related_name='employee_approvals', blank=True, null=True
    )
    supervisor = models.ForeignKey(
        Supervisor, on_delete=models.CASCADE,
        related_name='supervisor_approvals', blank=True, null=True
    )
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    level = models.IntegerField(default=1)
    approved_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.adjustment_request} | Level {self.level} | {self.status}"

    def save(self, *args, **kwargs):
        # Set approval timestamp
        if self.status in ['approved', 'rejected']:
            self.approved_date = timezone.localtime()

        super().save(*args, **kwargs)
        # Handle workflow progression
        if self.adjustment_request and self.status in ['approved', 'rejected']:
            self._handle_workflow_progression()

    def _handle_workflow_progression(self):
        adjustment = self.adjustment_request

        if self.status == 'rejected':
            # Reject the entire adjustment request
            adjustment.status = 'rejected'
            adjustment.approved_at = timezone.localtime()
            adjustment.save()
            # Reject ALL approvals when any supervisor rejects
            AdjustmentApproval.objects.filter(
                adjustment_request=adjustment
            ).update(
                status='rejected',
                approved_date=timezone.localtime()
            )
            
        elif self.status == 'approved':
            # Auto-approve all lower level approvals when a higher level approves
            AdjustmentApproval.objects.filter(
                adjustment_request=adjustment,
                level__lt=self.level,
                status='pending'
            ).update(
                status='approved',
                approved_date=timezone.localtime()
            )

            # Check if there are higher level approvals needed
            next_level = self.level + 1
            has_next_approval = AdjustmentApproval.objects.filter(
                adjustment_request=adjustment,
                level=next_level
            ).exists()

            if has_next_approval:
                # Move to next approval level
                adjustment.status = f'pending_L{next_level}'
                self.status = f'pending_L{next_level}'
                adjustment.save()
            else:
                # Final approval - update approved_at
                adjustment.status = 'approved'
                adjustment.approved_at = timezone.localtime()
                adjustment.save()

@receiver(post_save, sender=AttendanceAdjustment)
def create_approval_entries(sender, instance, created, **kwargs):
    if created and instance.employee:
        supervisors = Supervisor.objects.filter(employee=instance.employee).order_by('level')
        for supervisor in supervisors:
            AdjustmentApproval.objects.create(
                adjustment_request=instance,
                supervisor=supervisor,
                level=supervisor.level,
                status='pending',
            )

class AttendanceSummary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_semployee', blank=True, null=True)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='attendance_summaries', blank=True, null=True)
    late_by = models.DurationField(blank=True, null=True)
    early_out_by = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'attendance')
        ordering = ['-attendance__attendance_date']

    def __str__(self):
        return f"{self.employee.employee_name} - {self.attendance.attendance_date} - Late: {self.late_by} - Early Out: {self.early_out_by}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


@receiver(post_save, sender=ShiftInOut)
def create_attendance_summary(sender, instance, created, **kwargs):
    if not created or not instance.employee or not instance.attendance:
        return
    
    office_time = instance.employee.office_time if hasattr(instance.employee, 'office_time') else None
    if office_time and '-' in office_time:
        office_time_start_str, office_time_end_str = office_time.split('-')
        office_time_start = timezone.datetime.strptime(office_time_start_str.strip(), "%H:%M").time()
        office_time_end = timezone.datetime.strptime(office_time_end_str.strip(), "%H:%M").time()
    else:
        office_time_start = timezone.datetime.strptime("09:00", "%H:%M").time()
        office_time_end = timezone.datetime.strptime("18:00", "%H:%M").time()

    if (instance.in_time and instance.in_time < instance.shifting_in_start) or (instance.out_time and instance.out_time > instance.shifting_out_end):
        # Do not create summary, raise error
        raise ValidationError("Your leave history not created because you are out of shift in and out time range")

    skip_late_early = (
        instance.in_time and instance.out_time and 
        instance.in_time < office_time_start and
        instance.out_time > office_time_end
    )

    late_by = None
    early_out_by = None

    consideration = instance.consideration_time or timezone.timedelta(minutes=20)

    if not skip_late_early:
        # Calculate late_by
        if instance.in_time and office_time_start:
            diff = (
                timezone.datetime.combine(timezone.now().date(), instance.in_time) -
                timezone.datetime.combine(timezone.now().date(), office_time_start)
            )
            if diff >= consideration:
                late_by = diff
        # Calculate early_out_by
        if instance.out_time and office_time_end:
            diff = (
                timezone.datetime.combine(timezone.now().date(), office_time_end) -
                timezone.datetime.combine(timezone.now().date(), instance.out_time)
            )
            if diff >= consideration:
                early_out_by = diff

        AttendanceSummary.objects.create(
            employee=instance.employee,
            attendance=instance.attendance,
            late_by=late_by,
            early_out_by=early_out_by
        )




    




