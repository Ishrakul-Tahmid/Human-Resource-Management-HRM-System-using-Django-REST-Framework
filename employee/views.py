from django.shortcuts import render
from rest_framework import viewsets
from .models import Department, Designation, Nominee, Branch, Employee
from .serializers import DepartmentSerializer, DesignationSerializer, NomineeSerializer, BranchSerializer, EmployeeSerializer
from rest_framework.response import Response

# Create your views here.
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class NomineeViewSet(viewsets.ModelViewSet):
    queryset = Nominee.objects.all()
    serializer_class = NomineeSerializer

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    # lookup_field = 'employee_id'  # This is the key line you were missing

    # def list(self, request):
    #     """GET /employee/api/employees/ - Get all employees"""
    #     employees = Employee.objects.all()
    #     serializer = EmployeeSerializer(employees, many=True)
    #     return Response(serializer.data)
    
    # def create(self, request):
    #     """POST /employee/api/employees/ - Create a new employee"""
    #     serializer = EmployeeSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)
    
    # def retrieve(self, request, pk=None):  # Keep pk parameter but use lookup_field
    #     """GET /employee/api/employees/{employee_id}/ - Get single employee by employee_id"""
    #     try:
    #         # pk will contain the employee_id value due to lookup_field setting
    #         employee = Employee.objects.get(employee_id=pk)
    #         serializer = EmployeeSerializer(employee)
    #         return Response(serializer.data)
    #     except Employee.DoesNotExist:
    #         return Response({'error': 'Employee not found'}, status=404)
    
    # def update(self, request, pk=None):
    #     """PUT /employee/api/employees/{employee_id}/ - Update employee by employee_id"""
    #     try:
    #         employee = Employee.objects.get(employee_id=pk)
    #         serializer = EmployeeSerializer(employee, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=400)
    #     except Employee.DoesNotExist:
    #         return Response({'error': 'Employee not found'}, status=404)
    
    # def partial_update(self, request, pk=None):
    #     """PATCH /employee/api/employees/{employee_id}/ - Partial update employee by employee_id"""
    #     try:
    #         employee = Employee.objects.get(employee_id=pk)
    #         serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=400)
    #     except Employee.DoesNotExist:
    #         return Response({'error': 'Employee not found'}, status=404)
    
    # def destroy(self, request, pk=None):
    #     """DELETE /employee/api/employees/{employee_id}/ - Delete employee by employee_id"""
    #     try:
    #         employee = Employee.objects.get(employee_id=pk)
    #         employee.delete()
    #         return Response({'message': 'Employee deleted successfully'}, status=204)
    #     except Employee.DoesNotExist:
    #         return Response({'error': 'Employee not found'}, status=404)