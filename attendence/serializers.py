from rest_framework import serializers
from .models import Attendance, AttendanceAdjustment, AdjustmentApproval, AttendanceSummary, ShiftInOut
from django.utils import timezone
from zoneinfo import ZoneInfo

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.__str__', read_only=True)
    attendance_date = serializers.DateTimeField()

    class Meta:
        model = Attendance
        fields = ['id', 'employee_name', 'employee', 'attendance_date', 'status', 'created_at', 'updated_at']

    def validate_attendance_date(self, value):
        if timezone.is_naive(value):
            value = value.replace(tzinfo=ZoneInfo('Asia/Dhaka'))
        return value

class AttendanceAdjustmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.__str__', read_only=True)
    attendance_date = serializers.DateTimeField(source='attendance.attendance_date', read_only=True)

    class Meta:
        model = AttendanceAdjustment
        fields = '__all__'

class AdjustmentApprovalSerializer(serializers.ModelSerializer):
    adjustment_request_details = serializers.CharField(source='adjustment_request.__str__', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.__str__', read_only=True)

    class Meta:
        model = AdjustmentApproval
        fields = '__all__'

class ShiftInOutSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShiftInOut
        fields = ['id', 'name', 'employee', 'in_time', 'out_time', 'shifting_in_start', 'shifting_in_end', 'shifting_out_start', 'shifting_out_end', 'consideration_time', ]
        
    

class AttendanceSummarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.__str__', read_only=True)
    class Meta:
        model = AttendanceSummary
        fields = [field.name for field in AttendanceSummary._meta.fields] + ['employee_name']
    

    def validate(self, data):
        

        # Get employee and office time
        employee = data.get('employee') or getattr(self.instance, 'employee', None)
        office_time = None
        if employee and hasattr(employee, 'office_time'):
            office_time = employee.office_time
        if office_time and '-' in office_time:
            office_time_start_str, office_time_end_str = office_time.split('-')
            office_time_start = timezone.datetime.strptime(office_time_start_str.strip(), "%H:%M").time()
            office_time_end = timezone.datetime.strptime(office_time_end_str.strip(), "%H:%M").time()
        else:
            office_time_start = timezone.datetime.strptime("09:00", "%H:%M").time()
            office_time_end = timezone.datetime.strptime("18:00", "%H:%M").time()

        # Get in_time, out_time, shift windows, and consideration
        in_time = getattr('in_time', None)
        out_time = getattr('out_time', None)
        shifting_in_start = getattr( 'shifting_in_start', None)
        shifting_in_end = getattr('shifting_in_end', None)
        shifting_out_start = getattr('shifting_out_start', None)
        shifting_out_end = getattr( 'shifting_out_end', None)
        consideration = getattr('consideration_time', timezone.timedelta(minutes=20))

        # 1. Validation: in_time before shift in start OR out_time after shift out end
        if (in_time and in_time < shifting_in_start) or (out_time and out_time > shifting_out_end):
            raise serializers.ValidationError("Your leave history not created because you are out of shift in and out time range")

        # 2. If in_time before office_time_start and out_time after office_time_end, do not calculate late_by/early_out_by
        skip_late_early = (
            in_time and out_time and
            in_time < office_time_start and
            out_time > office_time_end
        )

        late_by = None
        early_out_by = None

        if not skip_late_early:
            # Calculate late_by
            if in_time and office_time_start:
                diff = (
                    timezone.datetime.combine(timezone.now().date(), in_time) -
                    timezone.datetime.combine(timezone.now().date(), office_time_start)
                )
                if diff > consideration:
                    late_by = diff
            # Calculate early_out_by
            if out_time and office_time_end:
                diff = (
                    timezone.datetime.combine(timezone.now().date(), office_time_end) -
                    timezone.datetime.combine(timezone.now().date(), out_time)
                )
                if diff > consideration:
                    early_out_by = diff

        # Attach calculated values to validated_data for use in create/update
        data['late_by'] = late_by
        data['early_out_by'] = early_out_by

        return data