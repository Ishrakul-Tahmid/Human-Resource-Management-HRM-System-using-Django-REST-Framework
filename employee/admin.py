from django.contrib import admin
from .models import Employee, Department, Designation, Nominee, Branch
from leave_management.models import Supervisor

class SupervisorInline(admin.TabularInline):
    model = Supervisor
    fk_name = 'employee'
    extra = 1

# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    inlines = [SupervisorInline]
    list_display = ('employee_id', 'employee_name', 'department', 'designation', 'status')
    def get_supervisors(self, obj):
        return ", ".join([str(sup) for sup in obj.supervisors.all()])
    get_supervisors.short_description = 'Supervisors'
    list_filter = ('department', 'designation', 'status', 'employment_type')
    search_fields = ('employee_id', 'employee_name__username', 'email_id')

    fieldsets = (
        (
            'Official Information (Admin only)', {
                'fields': (
                'employee_id', 'email_id', 'employee_name', 'designation', 'department', 'leave_group', 'employment_type',
                'location',
                'joining_date', 'probation_period', 'confirmation_date', 'supervisors',
                'office_days', 'office_time', 'office_mobile_number',
                'salary', 'rfid_code', 'status'
                )
            }
        ),
        (
            'Personal Information', {
                'fields': (
                'present_address', 'permanent_address', 'marital_status',
                'religion', 'blood_group', 'gender', 'personal_mobile',
                'personal_email', 'last_education', 'educational_institute',
                'last_job_experience', 'emergency_contact', 'nominee',
                'profile_picture'
                )
            }
        ),
        (
            'Access & Permissions', {
                'fields': ('system_access', 'security_clearance')
            }
        ),
        (
            'Work Preferences', {
                'fields': ('shift_preference',)
            }
        ),
        (
            'Optional Information(Admin Only)', {
                'fields': ('bank_details', 'resign_date', 'resign_reason'),
            }
        )
    )
    
    # Handle ManyToManyField with through model using filter_horizontal or inline
    # Since supervisors uses a through model, it will be handled by the intermediate model admin

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(Nominee)
admin.site.register(Branch)