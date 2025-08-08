from django.core.management.base import BaseCommand
from leave_management.models import LeavePolicy, LeaveGroup

class Command(BaseCommand):
    help = 'Seed unique Leave Policies per group, skipping duplicates within group'

    def handle(self, *args, **kwargs):
        # First create all required LeaveGroups
        groups = {
            'general_probation': 'General Staff (Probation)',
            'general_regular': 'General Staff (Regular)',
            'teachers_probation': 'Teachers (Probation)',
            'teachers_regular': 'Teachers (Regular)',
        }
        
        for group_id, group_name in groups.items():
            LeaveGroup.objects.get_or_create(
                id=group_id,
                defaults={'name': group_name}
            )

        # Use the choice keys instead of display names
        general_leave_types = [
            ("medical", 0, 15),        # Changed from "Medical Leave" to "medical"
            ("casual", 1, 12),         # Changed from "Casual Leave" to "casual"
            ("maternity", 30, 180),    # Changed from "Maternity Leave" to "maternity"
            ("paternity", 7, 15),      # Changed from "Paternity Leave" to "paternity"
            ("annual", 10, 30),        # Changed from "Annual Leave" to "annual"
            ("compensatory", 0, 5),    # Changed from "Compensatory Leave" to "compensatory"
            ("duty", 1, 10),           # Changed from "Duty Leave / On-Duty" to "duty"
            ("bereavement", 0, 7),     # Changed from "Bereavement Leave" to "bereavement"
            ("emergency", 0, 5),       # Changed from "Emergency Leave" to "emergency"
        ]

        teacher_leave_types = [
            ("medical", 0, 15),        # Changed from "Medical Leave" to "medical"
            ("casual", 1, 10),         # Changed from "Casual Leave" to "casual"
            ("maternity", 30, 180),    # Changed from "Maternity Leave" to "maternity"
            ("paternity", 7, 15),      # Changed from "Paternity Leave" to "paternity"
            ("bereavement", 0, 7),     # Changed from "Bereavement Leave" to "bereavement"
            ("duty", 1, 10),           # Changed from "Duty Leave / On-Duty" to "duty"
            ("study", 1, 5),           # Changed from "Study Leave" to "study"
        ]

        group_policy_map = {
            'general_probation': general_leave_types,
            'general_regular': general_leave_types,
            'teachers_probation': teacher_leave_types,
            'teachers_regular': teacher_leave_types,
        }

        for group_id, leave_types in group_policy_map.items():
            group = LeaveGroup.objects.get(id=group_id)
            
            for leave_type_key, apply_days, total_days in leave_types:
                if not LeavePolicy.objects.filter(
                    leave_type=leave_type_key,  # Now using the key instead of display name
                    leave_group=group
                ).exists():
                    validity_days = 30 if leave_type_key == "compensatory" else 0
                    
                    policy = LeavePolicy.objects.create(
                        leave_type=leave_type_key,  # Now using the key
                        leave_group=group,
                        apply_before_days=apply_days,
                        gender="any",
                        effective_from="joining",
                        total_leave_days=total_days,
                        max_days_per_request=30,
                        min_days_per_request=1,
                        allow_half_day=True,
                        count_holidays=False,
                        count_weekends=False,
                        is_active=True,
                        validity=validity_days
                    )
                    # Use get_leave_type_display() to show the human-readable name
                    self.stdout.write(self.style.SUCCESS(
                        f"Created '{policy.get_leave_type_display()}' policy for '{group.name}'"
                    ))
                else:
                    # For existing policies, get the display name for the message
                    existing_policy = LeavePolicy.objects.get(
                        leave_type=leave_type_key,
                        leave_group=group
                    )
                    self.stdout.write(self.style.WARNING(
                        f"Policy '{existing_policy.get_leave_type_display()}' already exists for '{group.name}' - skipped"
                    ))