from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, DesignationViewSet, NomineeViewSet, BranchViewSet, EmployeeViewSet

router = DefaultRouter()
router.register('department', DepartmentViewSet)
router.register('designation', DesignationViewSet)
router.register('nominee', NomineeViewSet)
router.register('branch', BranchViewSet)
router.register('employees', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
