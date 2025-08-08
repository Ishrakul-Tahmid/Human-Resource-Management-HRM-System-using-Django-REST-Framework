from rest_framework import serializers
from .models import Supervisor, LeavePolicy, LeaveRequest, LeaveApproval, AllowedLeaveTypes, CutOffDate, holiday
from django.utils import timezone
from datetime import date

# class LeaveGroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeaveGroup
#         fields = ['id', 'name']

class SupervisorSerializer(serializers.ModelSerializer):
    supervisor = serializers.StringRelatedField()
    employee = serializers.StringRelatedField()
    class Meta:
        model = Supervisor
        fields = ['id', 'employee', 'supervisor', 'level']

class LeavePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = ['id', 'leave_type', 'apply_before_days', 'total_leave_days', 'effective_from', 'allow_half_day']

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = holiday
        fields = ['name', 'from_date', 'to_date', 'days_count']

    def validate(self, data):
        from_date = data.get('from_date')
        to_date = data.get('to_date')

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError("From date cannot be after To date.")
        
        return data

class LeaveRequestSerializer(serializers.ModelSerializer):
    days_count = serializers.DecimalField(max_digits=4, decimal_places=1, default=0)
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'leave_policy', 'from_date', 'to_date', 'days_count']

    def validate(self, data):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        employee = data.get('employee')
        leave_policy = data.get('leave_policy')

        if leave_policy.gender:
            if leave_policy.gender != 'any' and leave_policy.gender != employee.gender:
                raise serializers.ValidationError('Leave policy gender does not match with employee gender')
        
        try:
            cutoff = CutOffDate.objects.first()
            cutoff_day = cutoff.cut_off_day if cutoff else 25
        except:
            cutoff_day = 25
            
        today = date.today()
        if today.day > cutoff_day and from_date.month == today.month and from_date.day<=cutoff_day:
            raise serializers.ValidationError(f"You cannot apply for leave for dates before or on the {cutoff_day}th of this month after the cutoff date.")
        
        if employee and leave_policy:
            last_approved = LeaveRequest.objects.filter(
                employee=employee,
                status='approved'
            ).order_by('-created_at').first()

            if last_approved:
                try:
                    allowed_sequence = AllowedLeaveTypes.objects.get(
                        leave_policy=last_approved.leave_policy
                    )
                    if not allowed_sequence.allowed_types.filter(pk=leave_policy.pk).exists():
                        raise serializers.ValidationError(
                            f'{leave_policy.get_leave_type_display()} leave cannot be applied after '
                            f'{last_approved.leave_policy.get_leave_type_display()} leave.'
                        )
                except AllowedLeaveTypes.DoesNotExist:
                    # No restrictions defined for this leave type
                    pass
        
        # Convert string dates to date objects if needed
        if isinstance(from_date, str):
            from datetime import datetime
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if isinstance(to_date, str):
            from datetime import datetime
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        # Only validate if all required fields are present
        if from_date and to_date:
            # Check date order
            if from_date > to_date:
                raise serializers.ValidationError("End date cannot be before start date")
            
            # Check leave policy effective date validations
            if employee and leave_policy:
                if leave_policy.effective_from == 'joining':
                    if employee.joining_date and from_date < employee.joining_date:
                        raise serializers.ValidationError('Leave cannot be applied before joining date.')
                
                elif leave_policy.effective_from == 'confirmation':
                    if employee.confirmation_date and from_date < employee.confirmation_date:
                        raise serializers.ValidationError('Leave cannot be applied before confirmation date.')
                
                elif leave_policy.effective_from == 'one_year':
                    if employee.joining_date:
                        one_year_anniversary = employee.joining_date + timezone.timedelta(days=365)
                        if from_date < one_year_anniversary:
                            raise serializers.ValidationError('Leave cannot be applied before one year of service.')
        
        return data

class LeaveApprovalSerializer(serializers.ModelSerializer):
    leave_request_details = LeaveRequestSerializer(source='leave_request', read_only=True)
    supervisor = serializers.StringRelatedField()  # Changed to use method field

    def validate(self, data):
        leave_request = data.get('leave_request')
        try:
            cutoff = CutOffDate.objects.first()
            cutoff_day = cutoff.cut_off_day if cutoff else 25
        except:
            cutoff_day = 25
            
        today = date.today()
        if today.day > cutoff_day and leave_request.from_date.month == today.month and leave_request.from_date.day<=cutoff_day:
            raise serializers.ValidationError(f"You cannot approve for leave for dates before or on the {cutoff_day}th of this month after the cutoff date.")
        
        return data

    class Meta:
        model = LeaveApproval
        fields = ['id', 'leave_request', 'supervisor', 'status', 'comments', 
                 'leave_request_details']
    
    # def get_supervisor_name(self, obj):
    #     if obj.supervisor and obj.supervisor.supervisor:
    #         return obj.supervisor.supervisor.employee_name
    #     return None

