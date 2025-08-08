from rest_framework import serializers
from .models import Department, Designation, Nominee, Branch, Employee
from django.core.exceptions import FieldDoesNotExist
from datetime import date


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'

class NomineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nominee
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

# --- Section: Official Information ---
from leave_management.serializers import SupervisorSerializer

class OfficialInfoSerializer(serializers.ModelSerializer):
    probation_period = serializers.IntegerField(default=3)
    supervisors = SupervisorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'email_id', 'employee_name', 'designation', 'department', 'leave_group',
            'location', 'joining_date', 'probation_period', 'confirmation_date',
            'supervisors', 'office_days', 'office_time', 'office_mobile_number',
            'employment_type', 'salary', 'rfid_code', 'status'
        ]

# --- Section: Personal Information ---
class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'present_address', 'permanent_address', 'marital_status', 'religion',
            'blood_group', 'gender', 'personal_mobile', 'personal_email',
            'last_education', 'educational_institute', 'last_job_experience',
            'emergency_contact', 'nominee', 'profile_picture'
        ]

# --- Section: Access & Permissions ---
class AccessPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['system_access', 'security_clearance']

# --- Section: Work Preferences ---
class WorkPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['shift_preference']

# --- Section: Optional Info ---
class OptionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['bank_details', 'resign_date', 'resign_reason']

class EmployeeSerializer(serializers.ModelSerializer):
    official_info = OfficialInfoSerializer(source='*', read_only=True)
    personal_info = PersonalInfoSerializer(source='*', read_only=True)
    access_permissions = AccessPermissionsSerializer(source='*', read_only=True)
    work_preferences = WorkPreferenceSerializer(source='*', read_only=True)
    optional_info = OptionalInfoSerializer(source='*', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'official_info',
            'personal_info',
            'access_permissions',
            'work_preferences',
            'optional_info'
        ]

    def create(self, validated_data):
        return Employee.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance