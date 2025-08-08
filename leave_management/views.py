from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from django.db.models import Max, Sum
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import models
from datetime import date


from employee.models import Employee
from .models import LeavePolicy, LeaveRequest, LeaveApproval, holiday
from .serializers import (
    LeavePolicySerializer, 
    LeaveRequestSerializer, 
    LeaveApprovalSerializer,
    HolidaySerializer
)

from rest_framework.views import APIView
from .utils import LeaveBalanceCalculator, LeaveTransfer
from .models import Supervisor


class LeavePolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Leave Policy CRUD operations
    """
    queryset = LeavePolicy.objects.all()
    serializer_class = LeavePolicySerializer

class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Holiday CRUD operations
    """
    queryset = holiday.objects.all()
    serializer_class = HolidaySerializer


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Leave Request CRUD operations
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    # @action(detail=False, methods=['get'], url_path='employee/(?P<employee_id>\d+)')
    # def employee_requests(self, request, employee_id=None):
    #     """Get all leave requests for a specific employee"""
    #     try:
    #         employee = Employee.objects.get(pk=employee_id)
    #         requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    #         serializer = self.get_serializer(requests, many=True)
    #         return Response(serializer.data)
    #     except Employee.DoesNotExist:
    #         return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    # @action(detail=False, methods=['get'], url_path='pending')
    # def pending_requests(self, request):
    #     """Get all pending leave requests"""
    #     # Fixed: Check for all pending statuses
    #     requests = LeaveRequest.objects.filter(
    #         status__in=['pending_L1', 'pending_L2', 'pending_L3']
    #     ).order_by('-created_at')
    #     serializer = self.get_serializer(requests, many=True)
    #     return Response(serializer.data)


class LeaveApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Leave Approval CRUD operations
    """
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer

    # @action(detail=False, methods=['get'], url_path='pending')
    # def pending_approvals(self, request):
    #     """Get all pending leave approvals"""
    #     approvals = LeaveApproval.objects.filter(
    #         status='pending'  # Fixed: Use approval status, not leave request status
    #     ).select_related('leave_request', 'leave_request__employee').order_by('-created_date')
    #     serializer = self.get_serializer(approvals, many=True)
    #     return Response(serializer.data)

    # @action(detail=True, methods=['post'], url_path='approve')
    # def approve_leave(self, request, pk=None):
    #     """Approve a specific leave request"""
    #     try:
    #         approval = self.get_object()
    #         approval.status = 'approved'
    #         approval.approve_date = timezone.now()
    #         approval.comments = request.data.get('comments', '')
    #         approval.save()
            
    #         # Update the leave request status based on approval level
    #         leave_request = approval.leave_request
    #         # Check if this is the final level of approval needed
    #         max_level = LeaveApproval.objects.filter(leave_request=leave_request).aggregate(
    #             max_level=models.Max('level')
    #         )['max_level']
            
    #         if approval.level == max_level:
    #             leave_request.status = 'approved'
    #         else:
    #             # Move to next level
    #             leave_request.status = f'pending_L{approval.level + 1}'
            
    #         leave_request.save()
            
    #         serializer = self.get_serializer(approval)
    #         return Response(serializer.data)
            
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=True, methods=['post'], url_path='reject')
    # def reject_leave(self, request, pk=None):
    #     """Reject a specific leave request"""
    #     try:
    #         approval = self.get_object()
    #         approval.status = 'rejected'
    #         approval.approve_date = timezone.now()
    #         approval.comments = request.data.get('comments', '')
    #         approval.save()
            
    #         # Update the leave request status
    #         approval.leave_request.status = 'rejected'
    #         approval.leave_request.save()
            
    #         serializer = self.get_serializer(approval)
    #         return Response(serializer.data)
            
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=['get'], url_path='supervisor/(?P<supervisor_id>\d+)')
    # def supervisor_requests(self, request, supervisor_id=None):
    #     """Get all leave requests assigned to a specific supervisor"""
    #     try:
    #         approvals = LeaveApproval.objects.filter(
    #             supervisor__supervisor_id=supervisor_id  # Fixed: Use correct field path
    #         ).select_related('leave_request', 'leave_request__employee').order_by('-created_date')
    #         serializer = self.get_serializer(approvals, many=True)
    #         return Response(serializer.data)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def ensure_date(val):
    from datetime import datetime, date

    if isinstance(val, date):
        return val  # already correct
    if isinstance(val, str):
        try:
            return date.fromisoformat(val)
        except ValueError:
            try:
                return datetime.strptime(val, '%Y-%m-%d').date()
            except Exception as e:
                raise ValueError(f"Could not parse date string '{val}': {e}")
    
    # Try coercing to string if it's something like datetime.datetime or other type
    try:
        val_str = str(val)
        return date.fromisoformat(val_str)
    except Exception as e:
        raise ValueError(f"Date value must be a string or date object. Got: {val} ({type(val)}). Error: {e}")


class EmployeeLeaveBalanceAPI(APIView):
    def get_employees_balance_by_supervisor(self, supervisor_employee_id, from_date, to_date):
        try:
            supervisor = Employee.objects.get(employee_id=supervisor_employee_id)
            supervisor_entries = Supervisor.objects.filter(supervisor=supervisor)

            if not supervisor_entries.exists():
                return []

            employee_ids = [entry.employee.id for entry in supervisor_entries]

            supervised_employees = Employee.objects.filter(
                id__in=employee_ids,
                status='active',
                leave_group__isnull=False
            )

            all_balances = []
            for employee in supervised_employees:
                try:
                    employee_balances = self.get_employee_balance(
                        employee.employee_id, from_date, to_date
                    )
                    if isinstance(employee_balances, Response):
                        all_balances.extend(employee_balances.data)
                    else:
                        all_balances.extend(employee_balances)
                except Exception:
                    continue

            return Response(all_balances)

        except Employee.DoesNotExist:
            raise Exception(f"Supervisor with employee_id {supervisor_employee_id} not found")
        except Exception as e:
            raise Exception(f"Error getting employees balance by supervisor: {str(e)}")

    def calculate_transferred_days(self, employee, policy, from_date, to_date):
        """Calculate transferred in/out days for a specific policy and period"""
        reset_start, reset_end = LeaveBalanceCalculator.get_leave_period_for_date(from_date)

        # Calculate transferred IN - days that came FROM other leave groups TO current leave group
        # This should match leave type and current leave group
        transferred_in_qs = LeaveTransfer.objects.filter(
            employee=employee,
            to_leave_policy__leave_type=policy.leave_type,
            to_leave_group=employee.leave_group,
            year__range=(reset_start, reset_end),
            is_reversed=False
        )
        transferred_in = transferred_in_qs.aggregate(total=Sum('days_transferred'))['total'] or 0

        # Calculate transferred OUT - days that went FROM current leave group TO other leave groups
        # This should match leave type and the from_leave_group should be current group
        transferred_out_qs = LeaveTransfer.objects.filter(
        employee=employee,
        from_leave_policy__leave_type=policy.leave_type,
        from_leave_group=employee.leave_group,  # Current group was the source
        year__range=(reset_start, reset_end),
        is_reversed=False
    ).exclude(
        to_leave_group=employee.leave_group  # Exclude transfers within same group
    )
        transferred_out = transferred_out_qs.aggregate(total=Sum('days_transferred'))['total'] or 0

        return float(transferred_in), float(transferred_out)

    def get_employee_balance(self, employee_id, from_date, to_date):
        try:
            from_date = ensure_date(from_date)
            to_date = ensure_date(to_date)

            employee = Employee.objects.get(employee_id=employee_id)
            if not employee.leave_group:
                return Response({"error": "Employee has no leave group assigned"}, status=400)

            policies = LeavePolicy.objects.filter(leave_group=employee.leave_group, is_active=True)
            balances = []

            for policy in policies:
                # Get the leave period for proper filtering
                reset_start, reset_end = LeaveBalanceCalculator.get_leave_period_for_date(from_date)
                
                # Calculate USED days - use already stored days_count from approved leaves
                # Filter by leave_type to include leaves from any leave group (for transfers)
                approved_leaves = LeaveRequest.objects.filter(
                    employee=employee,
                    leave_policy=policy,  # Match by leave type, not specific policy
                    status='approved',
                    from_date__gte=reset_start,  # Use reset period, not from_date/to_date
                    to_date__lte=reset_end
                )

                # Use the stored days_count instead of recalculating
                current_used = sum(
                    float(leave.days_count or 0) for leave in approved_leaves
                )

                # Calculate transferred days properly
                transferred_in, transferred_out = self.calculate_transferred_days(
                    employee, policy, from_date, to_date
                )

                # Calculate PENDING days - use stored days_count
                pending_leaves = LeaveRequest.objects.filter(
                    employee=employee,
                    leave_policy__leave_type=policy.leave_type,
                    status__in=['pending_L1', 'pending_L2', 'pending_L3'],
                    from_date__gte=reset_start,
                    to_date__lte=reset_end
                )

                pending_days = sum(
                    float(leave.days_count or 0) for leave in pending_leaves
                )

                # Probation adjustment calculation
                probation_adjustment = 0
                if hasattr(employee, 'joining_date') and employee.joining_date and employee.employment_type and employee.employment_type.endswith('probation'):
                    probation_end_date = employee.joining_date + timedelta(days=90)
                    if from_date <= probation_end_date:
                        probation_leaves = approved_leaves.filter(to_date__lte=probation_end_date)
                        probation_adjustment = sum(
                            float(leave.days_count or 0) for leave in probation_leaves
                        )

                # Calculate remaining balance
                # For transferred employees: their used days should be counted as transferred_in
                # so they don't get double-counted in both 'used' and 'transferred_in'
                remaining = max(
                    float(policy.total_leave_days or 0)
                    - current_used
                    - pending_days
                    - probation_adjustment
                    - transferred_in  # ADD transferred_in (these are used days from previous group)
                    + transferred_out,  # SUBTRACT transferred_out (days moved to other groups)
                    0
                )

                balances.append({
                    "employee_id": employee.employee_id,
                    "employee_name": str(employee),
                    "leave_policy_id": policy.id,
                    "leave_type": policy.leave_type,
                    "total_allowed": policy.total_leave_days,
                    "used": current_used,
                    "pending": pending_days,
                    "transferred_in": transferred_in,
                    "transferred_out": transferred_out,
                    "probation_adjustment": probation_adjustment,
                    "remaining": remaining,
                    "counts_holidays": policy.count_holidays,
                    "counts_weekends": policy.count_weekends,
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                })

            return Response(balances, status=200)

        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def get(self, request, employee_id=None, supervisor_id=None):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        year = request.query_params.get('year')
        
        try:
            # Date range handling
            if year:
                try:
                    year = int(year)
                    start_date, end_date = LeaveBalanceCalculator.get_leave_period_for_year(year)
                except ValueError:
                    return Response(
                        {"error": "Invalid year format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif from_date and to_date:
                try:
                    start_date = ensure_date(from_date)
                    end_date = ensure_date(to_date)
                except ValueError as e:
                    return Response(
                        {"error": f"Invalid date format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                start_date, end_date = LeaveBalanceCalculator.get_leave_period_for_date()

            if employee_id:
                return self.get_employee_balance(employee_id, start_date, end_date)
            elif supervisor_id:
                return self.get_employees_balance_by_supervisor(supervisor_id, start_date, end_date)
            else:
                return self.get_all_employees_balance(start_date, end_date)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_all_employees_balance(self, from_date, to_date):
        try:
            employees = Employee.objects.filter(status='active', leave_group__isnull=False)
            all_balances = []
            
            for employee in employees:
                balances = self.get_employee_balance(employee.employee_id, from_date, to_date)
                if balances.status_code == status.HTTP_200_OK:
                    all_balances.extend(balances.data)
            
            return Response(all_balances, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='by-supervisor/(?P<supervisor_id>\d+)')
    def by_supervisor(self, request, supervisor_id=None):
        """Get leave balances for all employees under a supervisor"""
        try:
            supervisor = get_object_or_404(pk=supervisor_id)
            
            # Get supervised employees through the Supervisor model
            supervised_employees = Employee.objects.filter(
                supervisor__supervisor=supervisor
            ).distinct()
            
            if not supervised_employees.exists():
                return Response(
                    {"detail": "No employees found under this supervisor"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get date range from query params or use current leave period
            from_date = request.query_params.get('from_date')
            to_date = request.query_params.get('to_date')
            year = request.query_params.get('year')
            
            if year:
                year = int(year)
                start_date, end_date = LeaveBalanceCalculator.get_leave_period_for_year(year)
            elif from_date and to_date:
                start_date = ensure_date(from_date)
                end_date = ensure_date(to_date)
            else:
                start_date, end_date = LeaveBalanceCalculator.get_leave_period_for_date()
            
            # Prepare response data
            response_data = {
                "supervisor_id": supervisor_id,
                "supervisor_name": supervisor.get_full_name(),
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "employees": []
            }
            
            # Get balances for each employee
            for employee in supervised_employees:
                employee_data = {
                    "employee_id": employee.employee_id,
                    "employee_name": employee.employee_name,
                    "designation": employee.designation.title if employee.designation else None,
                    "department": employee.department.name if employee.department else None,
                    "balances": self._get_employee_balances(employee, start_date, end_date)
                }
                response_data["employees"].append(employee_data)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_employee_balances(self, employee, from_date, to_date):
        """Helper method to get formatted balances for an employee"""
        # Reuse your existing get_employee_balance logic
        # This is just a wrapper to format the data consistently
        response = self.get_employee_balance(employee.employee_id, from_date, to_date)
        if response.status_code == status.HTTP_200_OK:
            return response.data
        return []