from django.shortcuts import render
from .models import Attendance, AttendanceAdjustment, AdjustmentApproval, ShiftInOut, AttendanceSummary
from .serializers import AttendanceSerializer, AttendanceAdjustmentSerializer, AdjustmentApprovalSerializer, ShiftInOutSerializer, AttendanceSummarySerializer
from rest_framework import viewsets
# Create your views here.
from employee.models import Employee
from leave_management.models import Supervisor
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    
class AttendanceAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = AttendanceAdjustment.objects.all()
    serializer_class = AttendanceAdjustmentSerializer

class AdjustmentApprovalViewSet(viewsets.ModelViewSet):
    queryset = AdjustmentApproval.objects.all()
    serializer_class = AdjustmentApprovalSerializer

class ShiftInOutViewSet(viewsets.ModelViewSet):
    queryset = ShiftInOut.objects.all()
    serializer_class = ShiftInOutSerializer

class AttendanceSummaryViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSummary.objects.all()
    serializer_class = AttendanceSummarySerializer

class EmployeeMonthlyAttendanceSummaryView(APIView):
    def get(self, request, employee_id, month_serial, *args, **kwargs):
        employee = get_object_or_404(Employee, employee_id=employee_id)
        summaries = AttendanceSummary.objects.filter(
            employee=employee,
            attendance__attendance_date__month=month_serial
        )

        total_attendance_days = summaries.count()
        total_late_by = sum([s.late_by.total_seconds() if s.late_by else 0 for s in summaries])
        total_early_out_by = sum([s.early_out_by.total_seconds() if s.early_out_by else 0 for s in summaries])

        def seconds_to_hms(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours:02}:{minutes:02}:{secs:02}"

        return Response({
            "employee": employee.id,
            "employee_name": str(employee),
            "total_attendance_days": total_attendance_days,
            "total_late_by": seconds_to_hms(total_late_by),
            "total_early_out_by": seconds_to_hms(total_early_out_by),
        })

class SupervisorMonthlyAttendanceSummaryView(APIView):
    def get(self, request, supervisor_employee_id, month_serial, *args, **kwargs):
        supervisor = Employee.objects.get(employee_id=supervisor_employee_id)
        supervisor_entries = Supervisor.objects.filter(supervisor=supervisor)

        if not supervisor_entries.exists():
            return []

        employee_ids = [entry.employee.employee_id for entry in supervisor_entries]

        supervised_employees = Employee.objects.filter(
            employee_id__in=employee_ids,
            status='active'
        )
        data = []

        for employee in supervised_employees:
            summaries = AttendanceSummary.objects.filter(
                employee__employee_id=employee.employee_id,
                attendance__attendance_date__month=month_serial
            )
            total_attendance_days = summaries.count()
            total_late_by = sum([s.late_by.total_seconds() if s.late_by else 0 for s in summaries])
            total_early_out_by = sum([s.early_out_by.total_seconds() if s.early_out_by else 0 for s in summaries])

            def seconds_to_hms(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                return f"{hours:02}:{minutes:02}:{secs:02}"

            data.append({
                "employee": employee.id,
                "employee_name": str(employee),
                "total_attendance_days": total_attendance_days,
                "total_late_by": seconds_to_hms(total_late_by),
                "total_early_out_by": seconds_to_hms(total_early_out_by),
            })
        return Response(data)
    
class SupervisorDailyAttendanceSummaryView(APIView):
    def get(self, request, supervisor_employee_id, *args, **kwargs):
        supervisor = Employee.objects.get(employee_id=supervisor_employee_id)
        supervisor_entries = Supervisor.objects.filter(supervisor=supervisor)

        if not supervisor_entries.exists():
            return []

        employee_ids = [entry.employee.employee_id for entry in supervisor_entries]

        supervised_employees = Employee.objects.filter(
            employee_id__in=employee_ids,
            status='active'
        )
        data = []

        for employee in supervised_employees:
            summaries = AttendanceSummary.objects.filter(employee=employee)
            for summary in summaries:
                data.append({
                    "employee": employee.id,
                    "employee_name": str(employee),
                    "attendance_date": summary.attendance.attendance_date,
                    "late_by": str(summary.late_by) if summary.late_by else "00:00:00",
                    "early_out_by": str(summary.early_out_by) if summary.early_out_by else "00:00:00",
                })
        return Response(data)
