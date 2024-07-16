from django_filters import filterset
from .models import *
import django_filters as filter_field
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



class CustomerFilter(filter_field.FilterSet):
    name = filter_field.CharFilter(field_name='name', lookup_expr='icontains')
    email = filter_field.CharFilter(field_name='email', lookup_expr='icontains')
    mobile_number = filter_field.CharFilter(field_name='mobile_number', lookup_expr='icontains')

    class Meta:
        model = Customer
        fields = ['name', 'email', 'mobile_number']


class HotelsFilter(filter_field.FilterSet):
    name = filter_field.CharFilter(field_name='name', lookup_expr='icontains')
    city = filter_field.CharFilter(field_name='city__name', lookup_expr='icontains')
    star_rating = filter_field.CharFilter(field_name='star_rating' , lookup_expr='icontains')
    class Meta:
        model = Hotel
        fields = ['name', 'city', 'star_rating']

class RoadTransportFilter(filter_field.FilterSet):
    vehicle_type = filter_field.CharFilter(field_name='vehicle_type', lookup_expr='icontains')
    seats = filter_field.CharFilter(field_name='seats', lookup_expr='icontains')
    # destination = filter_field.CharFilter(field_name='destination__name' , lookup_expr='icontains')
    # pickup_from = filter_field.CharFilter(field_name='pickup_from__name' , lookup_expr='icontains')
    class Meta:
        model = RoadTransportOption
        fields = '__all__'
class ActivityFilter(filter_field.FilterSet):
    activity_name = filter_field.CharFilter(field_name='activity_name', lookup_expr='icontains')
    activity_city = filter_field.CharFilter(field_name='activity_city__name', lookup_expr='icontains')
    category = filter_field.CharFilter(field_name='category' , lookup_expr='icontains')
    
    class Meta:
        model = Activity
        fields = '__all__'

class CustomizedPackageFilter(filter_field.FilterSet):
    customer = filter_field.CharFilter(field_name='customer__name', lookup_expr='icontains')
    activity_city = filter_field.CharFilter(field_name='activity_city__name', lookup_expr='icontains')
    category = filter_field.CharFilter(field_name='category' , lookup_expr='icontains')
    
    class Meta:
        model = CustomisedPackage
        fields = '__all__'

