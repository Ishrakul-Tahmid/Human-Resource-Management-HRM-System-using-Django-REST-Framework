

from django.contrib import admin
from django.utils import timezone
from .models import LeaveGroup, Supervisor, LeavePolicy, LeaveRequest, LeaveApproval, LeaveReset, AllowedLeaveTypes, CutOffDate, holiday
from .models import Supervisor
from employee.models import Employee
from django import forms
from .utils import LeaveTransfer
from django.core.exceptions import ValidationError

class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'from_date', 'to_date', 'days_count')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('-from_date',)

class LeaveResetAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_month', 'start_day', 'end_month', 'end_day', 'is_active', 'created_at', 'updated_at')
    search_fields = ('is_active', 'created_at', 'updated_at')
    ordering = ('created_at',)

class LeaveGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

class EmployeeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.employee_name}"
    
class SupervisorForm(forms.ModelForm):
    employee = EmployeeChoiceField(queryset=Employee.objects.all())
    supervisor = EmployeeChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = Supervisor
        fields = '__all__'
class LeaveTransferAdmin(admin.ModelAdmin):
    list_display = ('employee', 'from_leave_group', 'to_leave_group', 'days_transferred', 'created_at', 'from_leave_policy', 'to_leave_policy')
    # search_fields = ('employee__employee_name', 'from_leave_group__name', 'to_leave_group__name')
    class Meta:
        model = LeaveTransfer
        fields = '__all__'

class SupervisorAdmin(admin.ModelAdmin):
    form = SupervisorForm
    list_display = ('employee', 'supervisor', 'level')
    list_filter = ('level',)
    search_fields = ('employee__employee_name__username', 'supervisor__employee_name__username')
    raw_id_fields = ('employee', 'supervisor')
    
    def get_employee(self, obj):
        return obj.employee.employee_name
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'employee__employee_name',
            'supervisor__employee_name'
        )
from django import forms
from django.contrib import admin
from .models import LeavePolicy

@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ('leave_type', 'leave_group', 'total_leave_days', 'is_active')
    list_filter = ('leave_type', 'leave_group', 'is_active')
    search_fields = ('leave_type', 'leave_group__name')
    list_editable = ('is_active',)


class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'get_leave_type',
        'from_date',
        'to_date',
        'status',
        'days_count',
        'created_at',
        'is_half_day'
    )
    list_filter = (
        'status',
        'leave_policy__leave_type',
        'created_at'
    )
    search_fields = (
        'employee__employee_name',
        'leave_policy__leave_type'
    )
    readonly_fields = ('created_at', 'approved_at')
    date_hierarchy = 'from_date'
    actions = ['approve_requests', 'reject_requests']
    
    def get_leave_type(self, obj):
        return obj.leave_policy.get_leave_type_display()
    get_leave_type.short_description = 'Leave Type'

    def approve_requests(self, request, queryset):
        queryset.update(status='approved', approved_at=timezone.now())
    approve_requests.short_description = "Mark selected requests as approved"

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected', approved_at=timezone.now())
    reject_requests.short_description = "Mark selected requests as rejected"

class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = (
        'leave_request',
        'get_leave_type',
        'supervisor',
        'level',
        'status',
        'created_date',
        'approve_date'
    )
    list_filter = ('status', 'level')
    search_fields = (
        'leave_request__employee__employee_name',
        'supervisor__supervisor__username'
    )
    readonly_fields = ('created_date',)
    raw_id_fields = ('leave_request', 'supervisor')
    
    def get_leave_type(self, obj):
        return obj.leave_request.leave_policy.get_leave_type_display()
    get_leave_type.short_description = 'Leave Type'

@admin.register(AllowedLeaveTypes)
class AllowedLeaveTypesAdmin(admin.ModelAdmin):
    filter_horizontal = ('allowed_types',)
    list_display = ('leave_policy', 'get_allowed_types')
    
    def get_allowed_types(self, obj):
        return ", ".join([p.get_leave_type_display() for p in obj.allowed_types.all()])
    get_allowed_types.short_description = 'Allowed Types'

admin.site.register(LeaveGroup, LeaveGroupAdmin)
admin.site.register(Supervisor, SupervisorAdmin)
# admin.site.register(LeavePolicy, LeavePolicyAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
admin.site.register(LeaveApproval, LeaveApprovalAdmin)
admin.site.register(LeaveReset, LeaveResetAdmin)
admin.site.register(LeaveTransfer, LeaveTransferAdmin)
# admin.site.register(AllowedLeaveTypes, AllowedLeaveTypesAdmin)
admin.site.register(CutOffDate)
admin.site.register(holiday, HolidayAdmin)