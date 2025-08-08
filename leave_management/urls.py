from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import EmployeeLeaveBalanceAPI

router = DefaultRouter()
router.register(r'leave-policies', views.LeavePolicyViewSet)
router.register(r'leave-requests', views.LeaveRequestViewSet)
router.register(r'leave-approvals', views.LeaveApprovalViewSet)
router.register(r'holidays', views.HolidayViewSet)

# urlpatterns = [
#     path('api/', include(router.urls)),
#     path('leave-balance/employee/<str:employee_id>/', EmployeeLeaveBalanceAPI.as_view(), name='employee-leave-balance-detail'),
#     path('leave-balance/supervisor/<str:supervisor_id>/', EmployeeLeaveBalanceAPI.as_view(), name='supervisor-employee-leave-balance'),
#     path('leave-balance/', EmployeeLeaveBalanceAPI.as_view(), name='leave-balance-all'),
# ]
urlpatterns = [
    path('api/', include(router.urls)),

    # Leave balance endpoints
    path('leave-balance/', EmployeeLeaveBalanceAPI.as_view(), name='leave-balance-all'),
    path('leave-balance/employee/<str:employee_id>/', EmployeeLeaveBalanceAPI.as_view(), name='employee-leave-balance-detail'),
    path('leave-balance/supervisor/<str:supervisor_id>/', EmployeeLeaveBalanceAPI.as_view(), name='supervisor-employee-leave-balance'),
]