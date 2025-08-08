from django.db import models
from users.models import User
from datetime import timedelta
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Department"
    
class Designation(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title or "Unnamed Designation"
    

class Nominee(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    nid_no = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Nominee"

class Branch(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Branch"

class Employee(models.Model):
    # Official Information (Admin only)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email_id = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    employee_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_name', blank=True, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    leave_group = models.ForeignKey('leave_management.LeaveGroup', on_delete=models.SET_NULL, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=[
        ('general_regular', 'General(Regular)'), 
        ('general_probation', 'General(Probation)'),
        ('teacher_regular', 'Teacher(Regular)'), 
        ('teacher_probation', 'Teacher(Probation)'),
    ], default='general_probation', blank=True, null=True)
    location = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    probation_period = models.IntegerField(default=3, help_text="Probation period in months", blank=True, null=True)
    confirmation_date = models.DateField(blank=True,null=True)
    # filepath: c:\Leave Management\leave\employee\models.py
    supervisors = models.ManyToManyField(
        'leave_management.Supervisor',
        symmetrical=False,
        related_name='supervised_by',
        blank=True
    )
    office_days = models.CharField(max_length=100, blank=True, default="Monday-Friday")
    office_time = models.CharField(max_length=100, help_text="Format: HH:MM-HH:MM", blank=True, null=True, default="09:00-18:00")
    office_mobile_number = models.CharField(max_length=15, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rfid_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated')
    ], default='active')

    # Personal Information
    present_address = models.TextField(verbose_name="Present address", blank=True, null=True, max_length=500)
    permanent_address = models.TextField(verbose_name="Permanent address", blank=True, null=True, max_length=500)
    marital_status = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ])
    religion = models.CharField(max_length=50, blank=True, null=True, verbose_name="Religion", choices=[
        ('hindu', 'Hindu'),
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('sikh', 'Sikh'),
        ('buddhist', 'Buddhist'),
        ('jain', 'Jain'),
        ('other', 'Other')
    ])
    blood_group = models.CharField(max_length=10, verbose_name="Blood Group", choices=[
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
        ('unknown', 'Unknown')
    ], default='unknown')
    gender = models.CharField(max_length=10, 
                              choices=[ 
                                  ('any', 'Any'), 
                                  ('male', 'Male'),
                                  ('female', 'Female')
                                  ],
                                  default='any')
    personal_mobile = models.CharField(max_length=15, verbose_name="Personal Mobile Number", blank=True, null=True)
    personal_email = models.EmailField(verbose_name="Personal Email ID", max_length=254, blank=True, null=True)
    last_education = models.CharField(max_length=100, verbose_name="Last Education", blank=True, null=True)
    educational_institute = models.CharField(max_length=100, verbose_name="Educational Institute", blank=True, null=True)
    last_job_experience = models.TextField(verbose_name="Last job experience", blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, verbose_name="Emergency Contact", blank=True, null=True)
    nominee = models.ForeignKey(Nominee, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, verbose_name="Profile Picture upload")
    
    # Access & Permissions
    system_access = models.TextField(
        choices= User.ROLE_CHOICES, blank=True, null=True,
        verbose_name="System Access (E application)"
    )
    security_clearance = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Security Clearance Level (E application)"
    )
    
    # Work Preferences
    shift_preference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Self-Monitoring (default or pre-experienced units)"
    )
    
    # Optional Fields (Admin only)
    bank_details = models.TextField(blank=True)
    resign_date = models.DateField(null=True, blank=True, verbose_name="Resigned / Terminated Date")
    resign_reason = models.TextField(blank=True, verbose_name="Resigned / Terminated Reason")

    def __str__(self):
        return str(self.employee_name) if self.employee_name else f"Employee {self.employee_id or 'Unknown'}"


@receiver(pre_save, sender=Employee)
def set_employee_dates(sender, instance, **kwargs):
    from leave_management.models import LeaveGroup

    if instance.joining_date:
        probation_months = instance.probation_period if instance.probation_period is not None else 3
        instance.confirmation_date = instance.joining_date + timedelta(days=30 * probation_months)

    if instance.confirmation_date and instance.confirmation_date < timezone.now().date():
        try:
            if instance.employment_type == 'general_probation':
                instance.employment_type = 'general_regular'
                instance.leave_group = LeaveGroup.objects.get(name='general_regular')
            elif instance.employment_type == 'teacher_probation':
                instance.employment_type = 'teacher_regular'
                instance.leave_group = LeaveGroup.objects.get(name='teachers_regular')
        except LeaveGroup.DoesNotExist:
            # Handle case where LeaveGroup doesn't exist
            pass