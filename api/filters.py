from django_filters import filterset
from .models import *
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters

class EmployeeFilters(FilterSet):
    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('emp_name', 'emp_name'),
            ('emp_user__email', 'emp_email'),
            ('emp_user__mobile_number', 'emp_mobile_number'),
            ('emp_dob', 'emp_dob'),
        ),
        field_labels={
            'emp_name': 'Employee Name',
            'emp_user__email': 'Employee Email',
            'emp_user__mobile_number': 'Employee Mobile Number',
            'emp_dob': 'Date of Birth',
        }
    )
    class Meta:
        model=Employee
        fields='__all__'

