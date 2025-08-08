from tarfile import NUL
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from employee.models import Employee
User = get_user_model()
from datetime import date

class LeaveGroup(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Supervisor(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='supervised_employees')
    supervisor = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='supervisors_of')
    level = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('employee', 'supervisor', 'level')
        ordering = ['level']

    def __str__(self):
        return f"{self.supervisor} supervises {self.employee} (Level {self.level})"

    def save(self, *args, **kwargs):
        # Prevent circular supervisor relationships
        if self.employee == self.supervisor:
            raise ValidationError("An employee cannot be their own supervisor")
        
        # Ensure level is at least 1
        if not self.level or self.level < 1:
            self.level = 1
            
        super().save(*args, **kwargs)
        
        # # Update the employee's supervisors through the M2M relationship
        # if not self.employee.supervisors.filter(pk=self.supervisor.pk).exists():
        #     self.employee.supervisors.add(self.supervisor)
    
    

class LeavePolicy(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical Leave'),
        ('casual', 'Casual Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('annual', 'Annual Leave'),
        ('compensatory', 'Compensatory Leave'),
        ('duty', 'Duty Leave / On-Duty'),
        ('bereavement', 'Bereavement Leave'),
        ('emergency', 'Emergency Leave'),
        ('study', 'Study Leave'),
    ]
    
    GENDER_CHOICES = [('any', 'Any'), ('male', 'Male'), ('female', 'Female')]
    EFFECTIVE_FROM_CHOICES = [('joining', 'From Joining'), ('confirmation', 'After Confirmation'), ('one_year', 'After 1 Year Service')]
    
    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES,
        verbose_name="Leave Type"
    )
    leave_group = models.ForeignKey(LeaveGroup, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='any')
    apply_before_days = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0, blank=True, null=True)
    effective_from = models.CharField(max_length=20, choices=EFFECTIVE_FROM_CHOICES, blank=True, null=True)
    total_leave_days = models.PositiveIntegerField(default=0, blank=True, null=True)
    max_days_per_request = models.PositiveIntegerField(default=0, blank=True, null=True)
    min_days_per_request = models.PositiveIntegerField(default=0, blank=True, null=True)
    allow_half_day = models.BooleanField(default=False, blank=True, null=True)
    count_holidays = models.BooleanField(default=False, blank=True, null=True)
    count_weekends = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    validity = models.PositiveIntegerField(default=0, blank=True, null=True, help_text="Validity in days for the leave policy")
    
    def __str__(self):
        return f"{self.get_leave_type_display()} ({self.leave_group}) Policy"
    
    @property
    def leave_type_name(self):
        return self.get_leave_type_display()
    
    class Meta:
        verbose_name = "Leave Policy"
        verbose_name_plural = "Leave Policies"

class AllowedLeaveTypes(models.Model):
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, blank=True, null=True)
    allowed_types = models.ManyToManyField(LeavePolicy, blank=True, null=True, related_name='allowed_types')
    
    def __str__(self):
        return f" {self.leave_policy} - {self.allowed_types}"

class CutOffDate(models.Model):
    cut_off_day = models.PositiveSmallIntegerField(default=1)
    
    def __str__(self):
        return f"Cut-off Day: {self.cut_off_day} of each month"
    
class holiday(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    days_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"

    def clean(self):
        errors = []
        
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                errors.append("End date cannot be before start date")
        
        if errors:
            raise ValidationError(errors)
        
    def save(self, *args, **kwargs):
        # Calculate days count if both dates are provided
        if self.from_date and self.to_date:
            delta = (self.to_date - self.from_date).days + 1
            self.days_count = delta
        
        # Call clean method before saving
        self.full_clean()
        
        super().save(*args, **kwargs)

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_L1', 'Pending Level 1'),
        ('pending_L2', 'Pending Level 2'),
        ('pending_L3', 'Pending Level 3'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', null=True, blank=True)
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_L1', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    days_count = models.DecimalField(max_digits=4, decimal_places=1, default=0, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    is_half_day = models.BooleanField(default=False, blank=True, null=True)
    is_holiday = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_policy.get_leave_type_display()} ({self.status})"
    
    def is_holiday_range(self, date):
        holidays = holiday.objects.filter(from_date__lte=date, to_date__gte=date)
        return holidays.exists()
    
    def clean(self):
        errors = []

        if self.leave_policy:
            if self.leave_policy.gender != 'any' and self.leave_policy.gender != self.employee.gender:
                errors.append(
                    f"This leave policy is only applicable for {self.leave_policy.gender} employees, "
                    f"but {self.employee} is {self.employee.gender}."
                )
        
        try:
            cutoff = CutOffDate.objects.first()
            cutoff_day = cutoff.cut_off_day if cutoff else 25
        except:
            cutoff_day = 25

        today = date.today()
        if today.day > cutoff_day and self.from_date.month == today.month and self.from_date.day<=cutoff_day:
            errors.append(f"You cannot apply for leave for dates before or on the {cutoff_day}th of this month after the cutoff date.")
        if today.day < cutoff_day and self.from_date.month < today.month and self.from_date.day<=cutoff_day:
            errors.append(f"You cannot apply for leave for dates before or on the {cutoff_day}th of previous month before the cutoff date.")

        if self.employee and self.leave_policy:
            last_approved = LeaveRequest.objects.filter(
                employee=self.employee,
                status='approved'
            ).order_by('-created_at').first()

            if last_approved:
                try:
                    allowed_sequence = AllowedLeaveTypes.objects.get(
                        leave_policy=last_approved.leave_policy
                    )
                    if not allowed_sequence.allowed_types.filter(pk=self.leave_policy.pk).exists():
                        errors.append(
                            f'{self.leave_policy.get_leave_type_display()} leave cannot be applied after '
                            f'{last_approved.leave_policy.get_leave_type_display()} leave.'
                        )
                except AllowedLeaveTypes.DoesNotExist:
                    # No restrictions defined for this leave type
                    pass

        
        # Only validate dates if both are provided
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                errors.append("End date cannot be before start date")
            
            if self.leave_policy and self.leave_policy.effective_from == 'joining':
                if self.employee and self.employee.joining_date and self.from_date:
                    if self.from_date < self.employee.joining_date:
                        errors.append('Leave cannot be applied before joining date.')
            
            if self.leave_policy and self.leave_policy.effective_from == 'confirmation':
                if self.employee and self.employee.confirmation_date and self.from_date:
                    if self.from_date < self.employee.confirmation_date:
                        errors.append('Leave cannot be applied before confirmation date.') 
            
            if self.leave_policy and self.leave_policy.effective_from == 'one_year':
                if self.employee and self.employee.joining_date and self.from_date:
                    one_year_anniversary = self.employee.joining_date + timezone.timedelta(days=365)
                    if self.from_date < one_year_anniversary:
                        errors.append('Leave cannot be applied before one year of service.') 
    
        if errors:
            raise ValidationError(errors)

        
    def save(self, *args, **kwargs):
        # Call clean method before saving
        # self.clean()
        
        # Calculate days count if both dates are provided
        # if self.from_date and self.to_date:
        #     delta = (self.to_date - self.from_date).days + 1
        #     if delta == 1 and self.leave_policy and self.leave_policy.allow_half_day and self.is_half_day:
        #         self.days_count = 0.5
        #     elif delta == 1 and self.leave_policy and not self.leave_policy.allow_half_day:
        #         self.days_count = 1
        #     elif delta == 1 and self.leave_policy and self.leave_policy.allow_half_day and not self.is_half_day:
        #         self.days_count = 1
        #     else:
        #         self.days_count = delta
        if self.from_date and self.to_date:
            days = 0
            for i in range((self.to_date - self.from_date).days + 1):
                day = self.from_date + timezone.timedelta(days=i)

                if not self.is_holiday and self.is_holiday_range(day):
                    continue

                days += 0.5 if self.is_half_day and (self.to_date - self.from_date).days == 0 else 1
            self.days_count = days
            
        
        # Set approved_at timestamp when status changes to approved/rejected
        if self.pk and self.status in ['approved', 'rejected'] and not self.approved_at:
            self.approved_at = timezone.now()
        self.full_clean() 
        super().save(*args, **kwargs)
    


class LeaveApproval(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, blank=True, null=True)
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, blank=True, null=True)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending", blank=True, null=True)
    level = models.PositiveBigIntegerField(default=0, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    approve_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.leave_request} | Level-{self.level} | {self.status}"
            
    def clean(self):
        errors = []

        try:
            cutoff = CutOffDate.objects.first()
            cutoff_day = cutoff.cut_off_day if cutoff else 25
        except:
            cutoff_day = 25
            
        today = date.today()
        if today.day > cutoff_day and self.leave_request.from_date.month == today.month and self.leave_request.from_date.day<=cutoff_day:
            errors.append(f"You cannot approve for leave for dates before or on the {cutoff_day}th of this month after the cutoff date.")
            
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Track status changes for balance updates
        old_status = None
        if self.pk:
            try:
                old_instance = LeaveApproval.objects.get(pk=self.pk)
                old_status = old_instance.status
            except LeaveApproval.DoesNotExist:
                pass
        
        # Set approval timestamp
        if self.status in ['approved', 'rejected'] and not self.approve_date:
            self.approve_date = timezone.now()
        
        # Validate before saving
        self.clean()
        
        super().save(*args, **kwargs)
        
        # Handle workflow progression
        if self.leave_request and (self.status == 'approved' or self.status == 'rejected'):
            self._handle_workflow_progression()
        

    def _handle_workflow_progression(self):
        # try:
        #     self.leave_request.full_clean()
        #     self.leave_request.save()
        # except ValidationError as e:
        #     # Attach the error to this object so admin can display it
        #     raise ValidationError({'__all__': e.messages})
        leave_request = self.leave_request
        
        if self.status == 'rejected':
            # Reject the entire request
            leave_request.status = 'rejected'
            leave_request.approved_at = timezone.now()
            leave_request.save()
            
            # Reject ALL approvals when any supervisor rejects
            LeaveApproval.objects.filter(
                leave_request=leave_request
            ).update(
                status='rejected',
                approve_date=timezone.now()
            )
        elif self.status == 'approved':
            # Auto-approve all lower level approvals when a higher level approves
            LeaveApproval.objects.filter(
                leave_request=leave_request,
                level__lt=self.level,
                status='pending'
            ).update(
                status='approved',
                approve_date=timezone.now()
            )
            
            # Check if there are higher level approvals needed
            next_level = self.level + 1
            has_next_approval = LeaveApproval.objects.filter(
                leave_request=leave_request,
                level=next_level
            ).exists()
            
            if has_next_approval:
                # Move to next approval level
                leave_request.status = f'pending_L{next_level}'
                leave_request.save()
            else:
                # Final approval - update approved_at
                leave_request.status = 'approved'
                leave_request.approved_at = timezone.now()
                leave_request.save()



@receiver(post_save, sender=LeaveRequest)
def create_approval_entries(sender, instance, created, **kwargs):
    """Create approval entries for new leave requests"""
    if created and instance.employee:
        # Get supervisors ordered by level
        supervisors = Supervisor.objects.filter(employee=instance.employee).order_by('level')
        
        for sup in supervisors:
            LeaveApproval.objects.create(
                leave_request=instance,
                leave_policy=instance.leave_policy,
                supervisor=sup,
                level=sup.level,
                status='pending'
            )

class LeaveReset(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]
    start_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, default=1)
    start_day = models.PositiveSmallIntegerField(default=1)
    end_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, default=12)
    end_day = models.PositiveSmallIntegerField(default=31)
    is_active = models.BooleanField(default=True, help_text="If checked, this reset period is currently active.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Leave Reset Period"
        verbose_name_plural = "Leave Reset Periods"
    
    def _str_(self):
        return f"{self.get_start_month_display()} {self.start_day} to {self.get_end_month_display()} {self.end_day}"
    
    @classmethod
    def get_current_period(cls, date):
        """Get the current leave period for a given date"""
        # Get the first active reset period (if exists)
        reset_period = cls.objects.filter(is_active=True).first()
        # If no active reset period, return default calendar year
        if not reset_period:
            # Default to calendar year if no reset period is configured
            return (date.replace(month=1, day=1), date.replace(month=12, day=31))
        
        # Get the current year
        year = date.year
        
        # Create start and end dates
        start_date = date.replace(month=reset_period.start_month, day=reset_period.start_day)
        end_date = date.replace(month=reset_period.end_month, day=reset_period.end_day)
        
        # Handle cases where end month is earlier in the year than start month (e.g., June-May)
        if reset_period.end_month < reset_period.start_month:
            if date >= start_date:
                # Current period started this year, ends next year
                end_date = end_date.replace(year=year + 1)
            else:
                # Current period started last year, ends this year
                start_date = start_date.replace(year=year - 1)
        
        return start_date, end_date




