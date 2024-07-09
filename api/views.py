import json
import os
from django.shortcuts import render
from rest_framework import generics,status
from utils.common_view import BaseListCreateAPIView,BaseRetrieveUpdateDestroyAPIView 
from .models import *
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,DjangoModelPermissions
from utils.common_pagination import CustomPagination
from api import serializers
from django.db.models import F
from rest_framework import filters  
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EmployeeFilters
from rest_framework.response import Response
class EmployeeAttendanceListCreateAPI(BaseListCreateAPIView):
    queryset=EmployeeAttendance.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.EmployeeAttendanceSerializer




# Customer
class CustomerListCreateView(BaseListCreateAPIView):
    queryset=Customer.objects.select_related('country', 'state', 'city').all()
    authentication_classes=[JWTAuthentication]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    permission_classes=[IsAuthenticated]
    search_fields=['name','email','mobile_number']
    ordering_fields=['name','email','mobile_number']
    serializer_class=serializers.CustomerSerializer
    pagination_class=CustomPagination
    ordering='name'
    def get_queryset(self):
        req_user = self.request.user
        if req_user.role == 'Employee':
            if Employee.objects.filter(emp_user=req_user).exists():
                emp = Employee.objects.filter(emp_user=req_user).first()
                return self.queryset.filter(company=emp.company)
        elif req_user.role == 'Company':
            return self.queryset.filter(company__custom_user_id=req_user.id)
        elif req_user.role == 'Admin':
            return super().get_queryset()
        else:
            return Customer.objects.none() 
        

class CustomerUpdateDeleteView(BaseRetrieveUpdateDestroyAPIView):
    queryset= Customer.objects.all()
    authentication_classes=[JWTAuthentication]
    serializer_class=serializers.CustomerSerializer
    def get_queryset(self):
        req_user = self.request.user
        if req_user.role == 'Employee':
            if Employee.objects.filter(emp_user=req_user).exists():
                emp = Employee.objects.filter(emp_user=req_user).first()
                return self.queryset.filter(company=emp.company)
        elif req_user.role == 'Company':
            return self.queryset.filter(company__custom_user_id=req_user.id)
        elif req_user.role == 'Admin':
            return super().get_queryset()
        else:
            return Customer.objects.none() 

# Employee 
class EmployeeListCreateView(BaseListCreateAPIView):
    queryset=Employee.objects.all()
    authentication_classes=[JWTAuthentication]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter]
    permission_classes=[IsAuthenticated]
    pagination_class=CustomPagination
    filterset_class=EmployeeFilters
    search_fields=['emp_name','emp_user__email','emp_user__mobile_number']
    ordering_fields=['emp_name','emp_user__email','emp_user__mobile_number']
    serializer_class=serializers.EmployeeSerializer
    
    def get_queryset(self):
        
        req_user=self.request.user
        
        return self.queryset.filter(company__custom_user_id=req_user.id)
     

class EmployeeUpdateDeleteView(BaseRetrieveUpdateDestroyAPIView):
    queryset=Employee.objects.all()
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    serializer_class=serializers.EmployeeSerializer    

    def perform_destroy(self, instance):
        user = instance.emp_user
        if user:
            user.delete()
        # Delete the Employee instance
        return super().perform_destroy(instance)

class CountriesListView(generics.ListAPIView):
    queryset=Country.objects.all()
    serializer_class=serializers.CountriesSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter]
    search_fields=['name']
    ordering='name'


class StatesListView(generics.ListAPIView):
    queryset=States.objects.all()
    serializer_class=serializers.StateSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter]
    search_fields=['name']
    ordering='name'

    def get_queryset(self):
        country_id=self.kwargs.get('country_id')
        if country_id:
            return self.queryset.filter(country_id=country_id)

class CitiesListView(generics.ListAPIView):
    queryset=Cities.objects.all()
    serializer_class=serializers.CitieSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter]
    search_fields=['name']
    ordering='name'

    def get_queryset(self):
        state_id=self.kwargs.get('state_id')
      
        return self.queryset.filter(state_id=state_id)
    def get(self, request, *args, **kwargs):
        state_id=self.kwargs.get('state_id')

        queryset=self.queryset.filter(state_id=state_id)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query).values('id','name','state_id','country_id',country_name=F('country__name'),state_name=F('state__name'),)
            return Response(queryset)
    

        return Response(queryset.values('id','name','state_id','country_id',country_name=F('country__name'),state_name=F('state__name'),), status=status.HTTP_200_OK)
@api_view(['GET'])
@permission_classes([AllowAny])
def countries_data_entry(request):
    try:
        # Get the current directory of this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Build the absolute path to the countries.json file
        json_file_path = os.path.join(base_dir, 'data', 'countries.json')
        # Open and load the JSON file

        with open(json_file_path.replace('\\\\','\\'), encoding='utf-8') as f:
            countries = json.load(f)
            
            for country_data in countries:
                Country.objects.update_or_create(
                    name=country_data['name'],
                    defaults={
                        'id': country_data.get('id'),
                        'iso3': country_data.get('iso3'),
                        'iso2': country_data.get('iso2'),
                        'numeric_code': country_data.get('numeric_code'),
                        'phone_code': country_data.get('phone_code'),
                        'currency': country_data.get('currency'),
                        'currency_name': country_data.get('currency_name'),
                        'currency_symbol': country_data.get('currency_symbol'),
                        'region': country_data.get('region'),
                        'nationality': country_data.get('nationality'),
                        'emojiU': country_data.get('emojiU'),
                    }
                )
        
        return Response({'status': 'success', 'message': 'Countries data entry completed successfully.'})
    
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def states_data_entry(request):
    try:
        # Get the current directory of this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Build the absolute path to the countries.json file
        json_file_path = os.path.join(base_dir, 'data', 'states.json')
        # Open and load the JSON file

        with open(json_file_path.replace('\\\\','\\'), encoding='utf-8') as f:
            states = json.load(f)
            
            for states_data in states:
                if not States.objects.filter(name=states_data['name'],country_id=states_data.get('country_id'),).exists():
                    print(states_data['name'])
                    
                    States.objects.create(
                        name=states_data['name'],
                        country_id=states_data.get('country_id'),
                        id= states_data.get('id'),
                        state_code= states_data.get('state_code'),

                    )
                # States.objects.update_or_create(
                #     name=states_data['name'],
                #     country_id=states_data.get('country_id'),
                #     defaults={
                #         'id': states_data.get('id'),
                       
                #         'state_code': states_data.get('state_code'),
                    
                #     }
                # )
        
        return Response({'status': 'success', 'message': 'States data entry completed successfully.'})
    
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)
        
@api_view(['GET'])
@permission_classes([AllowAny])
def city_data_entry(request):
    try:
        # Get the current directory of this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Build the absolute path to the countries.json file
        json_file_path = os.path.join(base_dir, 'data', 'cities.json')
        # Open and load the JSON file

        with open(json_file_path.replace('\\\\','\\'), encoding='utf-8') as f:
            city = json.load(f)
            i=0
            for city_data in city:
                i= i+1
                if not Cities.objects.filter(name=city_data['name'],country_id=city_data.get('country_id'),state=city_data.get('state_id')).exists():
                    print(i,city_data['name'])
                    
                    defaults={
                        'id': city_data.get('id'),
                        'name': city_data.get('name'),
                        'country_id': city_data.get('country_id'),
                        'state_id': city_data.get('state_id'),

                      
                    }
                    Cities.objects.create(
                    **defaults
                    )
        
        return Response({'status': 'success', 'message': 'Cities data entry completed successfully.'})
    
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)
