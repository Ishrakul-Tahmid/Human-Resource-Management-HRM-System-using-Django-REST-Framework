from django.urls import path, include
from rest_framework import routers
from .views import AttendanceViewSet, AttendanceAdjustmentViewSet, AdjustmentApprovalViewSet, ShiftInOutViewSet, AttendanceSummaryViewSet, EmployeeMonthlyAttendanceSummaryView, SupervisorMonthlyAttendanceSummaryView, SupervisorDailyAttendanceSummaryView

router = routers.DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'attendance-adjustment', AttendanceAdjustmentViewSet, basename='attendance-adjustment')
router.register(r'adjustment-approval', AdjustmentApprovalViewSet, basename='adjustment-approval')
router.register(r'shift-in-out', ShiftInOutViewSet, basename='shift-in-out')
router.register(r'attendance-summary', AttendanceSummaryViewSet, basename='attendance-summary')

urlpatterns = [
    path('api/', include(router.urls)),

    path('employee/<str:employee_id>/<int:month_serial>/', EmployeeMonthlyAttendanceSummaryView.as_view(), name='employee-monthly-attendance-summary'),
    path('supervisor/<str:supervisor_employee_id>/<int:month_serial>/', SupervisorMonthlyAttendanceSummaryView.as_view(), name='supervisor-monthly-attendance-summary'),
    path('supervisor/<str:supervisor_employee_id>/', SupervisorDailyAttendanceSummaryView.as_view(), name='supervisor-daily-attendance-summary'),
]
