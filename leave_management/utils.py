from .models import LeaveReset, LeavePolicy, LeaveGroup, LeaveRequest
from employee.models import Employee
from django.utils import timezone
from datetime import date, timedelta
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
import uuid


class LeaveTransfer(models.Model):
    """Tracks leave transfers when employees change leave groups"""
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='leave_transfers', blank=True, null=True)
    from_leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, related_name='transfers_out', blank=True, null=True)
    to_leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, related_name='transfers_in', blank=True, null=True)
    from_leave_group = models.ForeignKey(LeaveGroup, on_delete=models.CASCADE, related_name='transfers_out', blank=True, null=True)
    to_leave_group = models.ForeignKey(LeaveGroup, on_delete=models.CASCADE, related_name='transfers_in', blank=True, null=True)
    days_transferred = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    transfer_date = models.DateField(auto_now_add=True)
    year = models.DateField(help_text="Year when the transfer occurred. Defaults to current year.", blank=True, null=True)
    transfer_identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    is_reversed = models.BooleanField(default=False)
    reversed_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.days_transferred} days transferred for {self.employee}"

    def save(self, *args, **kwargs):
        if self.year is None:
            self.year = timezone.now().date()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-transfer_date']
        indexes = [
            models.Index(fields=['employee', 'year']),
            models.Index(fields=['transfer_identifier']),
        ]


class LeaveBalanceCalculator:
    """Core leave balance calculation logic"""

    DAY_MAP = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }

    @classmethod
    def get_weekend_days(cls, employee):
        if not employee.office_days:
            return [5, 6]

        try:
            if '-' in employee.office_days:
                start, end = employee.office_days.lower().split('-')
                start_day = cls.DAY_MAP[start.strip()]
                end_day = cls.DAY_MAP[end.strip()]

                if start_day <= end_day:
                    working_days = list(range(start_day, end_day + 1))
                else:
                    working_days = list(range(start_day, 7)) + list(range(0, end_day + 1))

                return sorted(set(range(7)) - set(working_days))

        except (ValueError, KeyError):
            return [5, 6]

        return [5, 6]

    @classmethod
    def calculate_leave_days(cls, from_date, to_date, employee, policy, is_half_day=False):
        delta = to_date - from_date
        weekend_days = cls.get_weekend_days(employee)
        days = 0

        for i in range(delta.days + 1):
            current_day = from_date + timedelta(days=i)

            if not policy.count_weekends and current_day.weekday() in weekend_days:
                continue

            if policy.allow_half_day and is_half_day and delta.days == 0:
                return 0.5

            days += 1

        return days

    @classmethod
    def get_leave_period_for_date(cls, target_date=None):
        if target_date is None:
            target_date = date.today()
        return LeaveReset.get_current_period(target_date)

    @classmethod
    def get_leave_period_for_year(cls, year):
        return cls.get_leave_period_for_date(date(year, 1, 1))


@receiver(pre_save, sender=Employee)
def handle_leave_group_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_employee = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return

    if old_employee.leave_group == instance.leave_group:
        return

    current_date = timezone.now().date()
    reset_start, reset_end = LeaveReset.get_current_period(current_date)

    existing_transfers = LeaveTransfer.objects.filter(
        employee=instance,
        year__range=(reset_start, reset_end)
    ).order_by('created_at')

    if existing_transfers.exists():
        first_transfer = existing_transfers.first()
        original_leave_group = first_transfer.from_leave_group

        if instance.leave_group == original_leave_group:
            existing_transfers.delete()
            return

        last_transfer = existing_transfers.last()
        if last_transfer.to_leave_group == old_employee.leave_group:
            _update_existing_transfer(
                employee=instance,
                old_employee=old_employee,
                current_date=current_date,
                existing_transfer=last_transfer,
                reset_start=reset_start,
                reset_end=reset_end
            )
            return

    _create_or_update_transfers(instance, old_employee, current_date, reset_start, reset_end)


def _update_existing_transfer(employee, old_employee, current_date, existing_transfer, reset_start, reset_end):
    new_policies = LeavePolicy.objects.filter(
        leave_group=employee.leave_group,
        is_active=True
    )

    new_policy = new_policies.filter(
        leave_type=existing_transfer.to_leave_policy.leave_type
    ).first()

    if new_policy:
        total_used_days = _calculate_total_used_days_for_leave_type(
            employee,
            new_policy.leave_type,
            reset_start,
            reset_end
        )

        existing_transfer.to_leave_group = employee.leave_group
        existing_transfer.to_leave_policy = new_policy
        existing_transfer.days_transferred = total_used_days
        existing_transfer.notes = (
            f"Updated: {existing_transfer.from_leave_group}→"
            f"{old_employee.leave_group}→{employee.leave_group}"
        )
        existing_transfer.save()


def _create_or_update_transfers(employee, old_employee, current_date, reset_start, reset_end):
    old_policies = LeavePolicy.objects.filter(
        leave_group=old_employee.leave_group,
        is_active=True
    )

    new_policies = LeavePolicy.objects.filter(
        leave_group=employee.leave_group,
        is_active=True
    )

    for old_policy in old_policies:
        new_policy = new_policies.filter(
            leave_type=old_policy.leave_type
        ).first()

        if new_policy:
            existing_transfer = LeaveTransfer.objects.filter(
                employee=employee,
                from_leave_policy__leave_type=old_policy.leave_type,
                year__range=(reset_start, reset_end)
            ).order_by('-created_at').first()

            total_used_days = _calculate_total_used_days_for_leave_type(
                employee,
                old_policy.leave_type,
                reset_start,
                reset_end
            )

            if existing_transfer:
                existing_transfer.to_leave_group = employee.leave_group
                existing_transfer.to_leave_policy = new_policy
                existing_transfer.days_transferred = total_used_days
                existing_transfer.notes = (
                    f"Updated: {existing_transfer.from_leave_group}→"
                    f"{employee.leave_group}"
                )
                existing_transfer.save()
            else:
                if total_used_days > 0:
                    LeaveTransfer.objects.create(
                        employee=employee,
                        from_leave_policy=old_policy,
                        to_leave_policy=new_policy,
                        from_leave_group=old_employee.leave_group,
                        to_leave_group=employee.leave_group,
                        days_transferred=total_used_days,
                        year=current_date,
                        notes=f"Transfer: {old_employee.leave_group}→{employee.leave_group}"
                    )


def _calculate_total_used_days_for_leave_type(employee, leave_type, reset_start, reset_end):
    """
    Calculate total used days for a specific leave type within the reset period.
    Fixed to use the already calculated days_count from LeaveRequest instead of recalculating.
    """
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        leave_policy__leave_type=leave_type,
        status='approved',
        from_date__gte=reset_start,
        to_date__lte=reset_end
    )

    # Use the already calculated days_count instead of recalculating
    total_used = sum(
        leave_request.days_count or 0  # Handle None values
        for leave_request in approved_leaves
    )

    return total_used


def _calculate_used_days_for_policy(employee, policy, reset_start, reset_end):
    """
    Calculate used days for a specific policy within the reset period.
    Fixed to use the already calculated days_count from LeaveRequest instead of recalculating.
    """
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        leave_policy=policy,
        status='approved',
        from_date__gte=reset_start,
        to_date__lte=reset_end
    )

    # Use the already calculated days_count instead of recalculating
    total_used = sum(
        leave_request.days_count or 0  # Handle None values
        for leave_request in approved_leaves
    )

    return total_used