class LeaveBalanceCalculator:
    """Core leave balance calculation logic"""
    
    DAY_MAP = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    @classmethod
    def get_weekend_days(cls, employee):
        """Determine weekend days based on office_days"""
        if not employee.office_days:
            return [5, 6]  # Default to Saturday, Sunday
        
        try:
            if '-' in employee.office_days:  # Range format
                start, end = employee.office_days.lower().split('-')
                start_day = cls.DAY_MAP[start.strip()]
                end_day = cls.DAY_MAP[end.strip()]
                
                working_days = []
                current = start_day
                
                if start_day <= end_day:
                    working_days = list(range(start_day, end_day + 1))
                else:
                    working_days = list(range(start_day, 7)) + list(range(0, end_day + 1))
                
                return sorted(set(range(7)) - set(working_days))
                
        except (ValueError, KeyError):
            return [5, 6]  # Fallback to Sat/Sun
        
        return [5, 6]
    
    @classmethod
    def calculate_leave_days(cls, start_date, end_date, employee, policy, is_half_day=False):
        """Calculate effective leave days considering all rules"""
        delta = end_date - start_date
        weekend_days = cls.get_weekend_days(employee)
        days = 0
        
        # Single day leave
        if delta.days == 0:
            date = start_date
            is_weekend = date.weekday() in weekend_days
            # is_holiday = cls.is_holiday(date, employee)  # Uncomment when implemented
            
            if (policy.count_weekends or not is_weekend):  # and (policy.count_holidays or not is_holiday):
                if policy.allow_half_day and is_half_day:
                    return 0.5
                return 1
            return 0
        
        # Multi-day leave
        for i in range(delta.days + 1):
            date = start_date + timedelta(days=i)
            
            if not policy.count_weekends and date.weekday() in weekend_days:
                continue
                
            days += 1
        
        return days
    
    @classmethod
    def get_leave_period_for_date(cls, target_date=None):
        """Get the leave period for a given date, defaults to today"""
        if target_date is None:
            target_date = date.today()
        
        return LeaveReset.get_current_period(target_date)
    
    @classmethod
    def get_leave_period_for_year(cls, year):
        """get the leave period for a specific year"""
        reference_date = date(year, 1, 1)
        return cls.get_leave_period_for_date(reference_date)





@receiver(pre_save, sender=Employee)
def handle_leave_group_change(sender, instance, **kwargs):
    """Handle leave group changes for employees"""
    if not instance.pk:  # New employee, nothing to transfer
        return
        
    try:
        old_employee = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return
        
    # No change in leave group
    if old_employee.leave_group == instance.leave_group:
        return
        
    current_date = timezone.now().date()
    reset_start, reset_end = LeaveReset.get_current_period(current_date)
    
    # Process the leave group change
    process_leave_group_change(instance, old_employee, current_date, reset_start, reset_end)


def process_leave_group_change(employee, old_employee, current_date, reset_start, reset_end):
    """Process leave group changes with proper transfer logic"""
    
    # Get existing transfers for this employee in current period
    existing_transfers = LeaveTransfer.objects.filter(
        employee=employee,
        year__range=(reset_start, reset_end),
        is_reversed=False
    ).order_by('created_at')
    
    if existing_transfers.exists():
        # Check if returning to original group
        first_transfer = existing_transfers.first()
        if employee.leave_group == first_transfer.from_leave_group:
            # Returning to original group - reverse all transfers
            reverse_all_transfers(employee, existing_transfers)
            return
        
        # Otherwise, create new transfers for the new group
        create_transfers_for_new_group(employee, old_employee, current_date, reset_start, reset_end)
    else:
        # First time changing group - create initial transfers
        create_initial_transfers(employee, old_employee, current_date, reset_start, reset_end)


def reverse_all_transfers(employee, transfers):
    """Reverse all transfers when employee returns to original group"""
    transfer_identifier = uuid.uuid4()
    
    for transfer in transfers:
        LeaveTransfer.objects.create(
            employee=employee,
            from_leave_policy=transfer.to_leave_policy,
            to_leave_policy=transfer.from_leave_policy,
            from_leave_group=transfer.to_leave_group,
            to_leave_group=transfer.from_leave_group,
            days_transferred=-transfer.days_transferred,  # Negative to reverse
            year=transfer.year,
            transfer_identifier=transfer_identifier,
            is_reversed=True,
            reversed_by=transfer,
            notes=f"Reversed: Employee returned to original group {transfer.from_leave_group}"
        )
    
    # Mark original transfers as reversed
    transfers.update(is_reversed=True)


def create_initial_transfers(employee, old_employee, current_date, reset_start, reset_end):
    """Create initial transfers when employee first changes leave group"""
    old_policies = LeavePolicy.objects.filter(
        leave_group=old_employee.leave_group,
        is_active=True
    )
    
    new_policies = LeavePolicy.objects.filter(
        leave_group=employee.leave_group,
        is_active=True
    )
    
    transfer_identifier = uuid.uuid4()
    
    for old_policy in old_policies:
        # Find matching policy in new group
        new_policy = new_policies.filter(leave_type=old_policy.leave_type).first()
        
        if new_policy:
            # Calculate used days for this leave type
            used_days = calculate_used_days_for_leave_type(
                employee, old_policy.leave_type, reset_start, reset_end
            )
            
            # Only create transfer if there are used days
            if used_days > 0:
                LeaveTransfer.objects.create(
                    employee=employee,
                    from_leave_policy=old_policy,
                    to_leave_policy=new_policy,
                    from_leave_group=old_employee.leave_group,
                    to_leave_group=employee.leave_group,
                    days_transferred=used_days,
                    year=current_date,
                    transfer_identifier=transfer_identifier,
                    notes=f"Initial transfer: {old_employee.leave_group} → {employee.leave_group}"
                )


def create_transfers_for_new_group(employee, old_employee, current_date, reset_start, reset_end):
    """Create transfers when moving from current group to a new group"""
    old_policies = LeavePolicy.objects.filter(
        leave_group=old_employee.leave_group,
        is_active=True
    )
    
    new_policies = LeavePolicy.objects.filter(
        leave_group=employee.leave_group,
        is_active=True
    )
    
    transfer_identifier = uuid.uuid4()
    
    for old_policy in old_policies:
        new_policy = new_policies.filter(leave_type=old_policy.leave_type).first()
        
        if new_policy:
            # Calculate total used days for this leave type
            used_days = calculate_used_days_for_leave_type(
                employee, old_policy.leave_type, reset_start, reset_end
            )
            
            if used_days > 0:
                # Check if there's an existing transfer for this leave type
                existing_transfer = LeaveTransfer.objects.filter(
                    employee=employee,
                    to_leave_policy__leave_type=old_policy.leave_type,
                    year__range=(reset_start, reset_end),
                    is_reversed=False
                ).order_by('-created_at').first()
                
                if existing_transfer:
                    # Update existing transfer
                    existing_transfer.to_leave_group = employee.leave_group
                    existing_transfer.to_leave_policy = new_policy
                    existing_transfer.days_transferred = used_days
                    existing_transfer.notes = f"Updated: {existing_transfer.from_leave_group} → {employee.leave_group}"
                    existing_transfer.save()
                else:
                    # Create new transfer
                    LeaveTransfer.objects.create(
                        employee=employee,
                        from_leave_policy=old_policy,
                        to_leave_policy=new_policy,
                        from_leave_group=old_employee.leave_group,
                        to_leave_group=employee.leave_group,
                        days_transferred=used_days,
                        year=current_date,
                        transfer_identifier=transfer_identifier,
                        notes=f"New transfer: {old_employee.leave_group} → {employee.leave_group}"
                    )


def calculate_used_days_for_leave_type(employee, leave_type, reset_start, reset_end):
    """Calculate total used days for a specific leave type within the reset period"""
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        leave_policy__leave_type=leave_type,
        status__in=['approved', 'pending'],
        from_date__gte=reset_start,
        to_date__lte=reset_end
    )
    
    total_used = 0
    for leave_request in approved_leaves:
        days = LeaveBalanceCalculator.calculate_leave_days(
            leave_request.from_date,
            leave_request.to_date,
            employee,
            leave_request.leave_policy,
            leave_request.is_half_day
        )
        total_used += days
    
    return total_used