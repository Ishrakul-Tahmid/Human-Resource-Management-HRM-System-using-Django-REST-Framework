from django.contrib import admin
from .models import Attendance, AttendanceAdjustment, AdjustmentApproval, AttendanceSummary, ShiftInOut

class ShiftInOutAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee', 'in_time', 'out_time')
    search_fields = ('employee__name', )
    list_filter = ('employee',)

# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'attendance_date', 'status', 'created_at', 'updated_at')
    search_fields = ('employee__name', 'rfid_no', 'status')
    list_filter = ('status', 'attendance_date')

class AttendanceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'attendance', 'adjustment_type', 'timeframe_start', 'timeframe_end', 'status', 'approved_at')
    search_fields = ('employee__name', 'adjustment_type', 'status')
    list_filter = ('status', 'adjustment_type')

class AdjustmentApprovalAdmin(admin.ModelAdmin):
    list_display = ('adjustment_request', 'supervisor', 'status', 'approved_date')
    search_fields = ('adjustment_request__employee__name', 'supervisor__name', 'status')
    list_filter = ('status',)

class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 
        'attendance', 
        'late_by', 
        'early_out_by'
    )
    search_fields = (
        'employee__employee_name', 
        'attendance__attendance_date'
    )
    list_filter = (
        'employee__employee_name', 
        'attendance__attendance_date'
    )

admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AttendanceAdjustment, AttendanceAdjustmentAdmin)    
admin.site.register(AdjustmentApproval, AdjustmentApprovalAdmin)
admin.site.register(AttendanceSummary, AttendanceSummaryAdmin)
admin.site.register(ShiftInOut, ShiftInOutAdmin)
