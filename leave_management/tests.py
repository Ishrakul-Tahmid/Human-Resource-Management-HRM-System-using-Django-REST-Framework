
from django.test import TestCase
from django.contrib.auth import get_user_model
from employee.models import Employee
from leave_management.models import LeaveGroup, LeavePolicy, LeaveRequest
from leave_management.views import EmployeeLeaveBalanceAPI
from datetime import date, timedelta

# Create your tests here.

class LeaveBalanceTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password'
        )
        self.leave_group = LeaveGroup.objects.create(name='Test Group')
        self.employee = Employee.objects.create(
            employee_id='123',
            employee_name='Test Employee',
            user=self.user,
            leave_group=self.leave_group,
            joining_date=date(2023, 1, 1)
        )
        self.leave_policy = LeavePolicy.objects.create(
            leave_type='emergency',
            total_leave_days=5,
            leave_group=self.leave_group,
            is_active=True
        )

    def test_multiple_approved_leaves(self):
        # Create and approve the first leave request
        leave1 = LeaveRequest.objects.create(
            employee=self.employee,
            leave_policy=self.leave_policy,
            from_date=date(2024, 2, 1),
            to_date=date(2024, 2, 2),
            leave_days=2,
            status='approved'
        )

        # Create and approve the second leave request
        leave2 = LeaveRequest.objects.create(
            employee=self.employee,
            leave_policy=self.leave_policy,
            from_date=date(2024, 3, 5),
            to_date=date(2024, 3, 5),
            leave_days=1,
            status='approved'
        )

        # Calculate the leave balance
        calculator = EmployeeLeaveBalanceAPI()
        balance_data = calculator.get_employee_balance(
            self.employee.employee_id,
            date(2024, 1, 1),
            date(2024, 12, 31)
        )

        # Verify the results
        self.assertEqual(len(balance_data), 1)
        balance = balance_data[0]
        self.assertEqual(balance['total_used'], 3)
        self.assertEqual(balance['remaining'], 2)