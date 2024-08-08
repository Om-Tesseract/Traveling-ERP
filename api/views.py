import datetime
import json
import os
from django.db import transaction
from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from utils.common_view import BaseListCreateAPIView,BaseRetrieveUpdateDestroyAPIView 
from .models import *
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly,DjangoModelPermissions
from utils.common_pagination import CustomPagination
from api import serializers
from django.db.models import F,Q,Value,Sum,Count
from django.db.models.functions import Concat
from rest_framework import filters  
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EmployeeFilters,CustomerFilter,HotelsFilter,RoadTransportFilter,ActivityFilter
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import re
from django.db.models.functions import TruncMonth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
chrome_options = webdriver.ChromeOptions()
              # Uncomment the next line if you want to run Chrome in headless mode
chrome_options.add_argument("--headless")
# chrome_options.add_experimental_option('detach',True)
chromedriver_path = r'./chromedriver/chromedriver.exe'
# Set up the Chrome WebDriver using the webdriver_manager
service = ChromeService(chromedriver_path)
# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_companies(request):
    companies = Company.objects.all()
    serializer = serializers.CompanySerializer(companies, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_company(request):
    data = request.data.copy()
    
    # Extract user-related data
    user_data = {
        'username': data.get('username'),
        'password': data.get('password'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'nick_name': data.get('nick_name'),
        'mobile_number': data.get('mobile_number'),
        'address1': data.get('address1'),
        'address2': data.get('address2'),
        'email': data.get('email'),
        'role': data.get('role'),
    }
    
    try:
        user = CustomUser.objects.create(**user_data)
        user.set_password(user_data['password'])
        user.save()
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    data['custom_user'] = user.id

    for key, value in request.FILES.items():
        data[key] = value
    
    serializer = serializers.CompanySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        user.delete()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def update_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "GET":
        serializer = serializers.CompanySerializer(company)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = serializers.CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.custom_user.delete()
    company.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#dashboard view
class DashboardListView(APIView):
        
    def get(self,request,*args, **kwargs):
        req_user = self.request.user
        company=None
        if req_user.role == 'Employee':
            if Employee.objects.filter(emp_user=req_user).exists():
                company = Employee.objects.filter(emp_user=req_user).first().company
                
        elif req_user.role == 'Company':
            company= Company.objects.filter(custom_user_id=req_user.id).first()
        if company is not None:
            total_customer= Customer.objects.filter(company=company).count()
            total_pending_itinerary= CustomisedPackage.objects.filter(company=company,status="PENDING").count()
            total_completed_itinerary= CustomisedPackage.objects.filter(company=company,status="COMPLETED").count()
            total_itinerary= CustomisedPackage.objects.filter(company=company).count()
            current_year = datetime.datetime.now().year
            monthly_itinerary_counts = CustomisedPackage.objects.filter(
                company=company,
                leaving_on__year=current_year
            ).values('leaving_on__month').annotate(count=Count('id')).order_by('leaving_on__month')

            monthly_counts = {i: 0 for i in range(1, 13)}  # Initialize dictionary for all months
            for entry in monthly_itinerary_counts:
                monthly_counts[entry['leaving_on__month']] = entry['count']
            state_package_counts = CityNight.objects.filter(
                package__company=company,
                package__leaving_on__year=current_year
            ).values('city__state__name').annotate(package_count=Count('package', distinct=True)).order_by('city__state__name')
            
            state_counts = {item['city__state__name']: item['package_count'] for item in state_package_counts}

            context={
                "total_customers": total_customer,
                "total_pending_itinerary":total_pending_itinerary,
                "total_completed_itinerary":total_completed_itinerary,
                "total_itinerary":total_itinerary,
                 "monthly_itinerary_counts": monthly_counts,
                 "state_package_counts": state_counts
            }

         
            return Response(context)
        else:
            return Response({"message": "Couldn't find company"})
# EmployeeAttendance view
class EmployeeAttendanceListCreateAPI(BaseListCreateAPIView):
    queryset=EmployeeAttendance.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.EmployeeAttendanceSerializer
    search_fields=['status','employee__emp_name']
    filterset_fields=['date_of_attendance','status']

#activity
class ActivityListCreateAPI(BaseListCreateAPIView):
    queryset=Activity.objects.all().exclude(activity_name__icontains="Departure from ")
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.ActivitySerializer
    search_fields=['activity_name','activity_city__name']
    # pagination_class=CustomPagination
    filterset_class=ActivityFilter
    ordering='sequence'

class ActivityUpdateDestroyAPI(BaseRetrieveUpdateDestroyAPIView):
    queryset=Activity.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.ActivitySerializer


class HotelDetailsUpdateView(generics.UpdateAPIView,generics.DestroyAPIView):    
    queryset=HotelDetails.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class=serializers.HotelDetailsUpdateSerializer

    

@api_view(['GET'])
def RoomTypeListView(request):
    roomtype=RoomType.objects.all().values('rnm').distinct()
    return Response(roomtype)
@api_view(['GET'])
def MealPlanListView(request):
    meal_plan=RoomType.objects.all().values('meal_plan').distinct()
    return Response(meal_plan)

class ItineraryUpdateDeleteView(BaseRetrieveUpdateDestroyAPIView):
    queryset=Itinerary.objects.all()
    serializer_class=serializers.ItinerarySerializer
    permission_classes=[IsAuthenticated]

class ItineraryChangeDayView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        iter_id = kwargs.get('pk')
        swapdate = request.data.get('swapdate')

        if not swapdate:
            return Response({"error": "swapdate is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the current itinerary
        current_itinerary = get_object_or_404(Itinerary, pk=iter_id)

        try:
            # Find the itinerary with the swapdate
            swap_itinerary = Itinerary.objects.get(days=swapdate, package=current_itinerary.package)
        except Itinerary.DoesNotExist:
            return Response({"error": "Itinerary with the specified swapdate does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Swap the activities
        with transaction.atomic():
            current_activities = list(current_itinerary.itinerary_activity.all())
            swap_activities = list(swap_itinerary.itinerary_activity.all())

            # Update current activities to point to swap itinerary
            for activity in current_activities:
                activity.itinerary = swap_itinerary
                activity.save()

            # Update swap activities to point to current itinerary
            for activity in swap_activities:
                activity.itinerary = current_itinerary
                activity.save()

        return Response({"success": "Activities swapped successfully"}, status=status.HTTP_200_OK)
# class SummaryTripApi(generics.ListAPIView):
#     permission_classes=[IsAuthenticated]

#     def get(self, request, *args, **kwargs):
            
#         return 
    

#customised package add 
class CustomizedPackageListCreateAPI(BaseListCreateAPIView):
    queryset=CustomisedPackage.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.CustomisedPackageSerializer
    pagination_class=CustomPagination


class CustomizedPackageUpdateDestroyAPI(BaseRetrieveUpdateDestroyAPIView):
    queryset=CustomisedPackage.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.CustomisedPackageSerializer

# list, Retrive Data
class CustomizePackageListView(APIView):
    pagination_class = CustomPagination

    def get(self,request, *args, **kwargs):
        if self.kwargs.get('package_id'):
            package_id=self.kwargs.get('package_id')
            
            hoteldetails=HotelDetails.objects.filter(package_id=package_id).values(
                'id','hotel','facilities','meal_plans','room',
                'check_in_date','check_out_date','room_type','number_of_rooms',
                'total_price','additional_requests',
                hotel_name=F('hotel__name'),hotel_address=F('hotel__address'),
                hotel_city=F('hotel__city'),hotel_state=F('hotel__city__state__name'),
                hotel_country=F('hotel__city__country__name'),
                hotel_city_name=F('hotel__city__name'),hotel_star_rating=F('hotel__star_rating'),
                image_url=F('hotel__image_url'),ln=F('hotel__ln'),lt=F('hotel__lt'),
                contact_info=F('hotel__contact_info'),
                review_rate=F('hotel__rate'),
                
            )
            for ht in hoteldetails:
                room_types=RoomType.objects.filter(hotel_id=ht.get('hotel'))
                # ht['meal_plan']=room_types.filter(rnm=ht.get('room_type')).first().meal_plan if room_types.filter(rnm=ht.get('room_type')).first() else None
                # ht['amenity']=json.load(room_types.filter(rnm=ht.get('room_type')).first().amenity) if room_types.filter(rnm=ht.get('room_type')).first() else None
                # try:
                #     if room_types.filter(rnm=ht.get('room_type')).first().amenity:
                #         amenity_list = json.loads(room_types.filter(rnm=ht.get('room_type')).first().amenity)
                #         ht['amenity'] = amenity_list
                # except json.JSONDecodeError as e:
                #     # Handle JSON decoding error
                #     print(f"Error decoding JSON: {e}")
                #     ht['amenity'] = None
                # except AttributeError as e:
                #     # Handle attribute error if the filter or first() fails
                #     print(f"Attribute error: {e}")
                #     ht['amenity'] = None
                ht['room_types']=room_types.values()


            package=CustomisedPackage.objects.filter(id=package_id).values(
                'id','number_of_rooms','leaving_on','number_of_adults','number_of_children',
                'interests','who_is_travelling','pregnant_women','elderly_people','with_walking_difficulty',
                'teenager','women_only','men_only','star_rating','add_transfers','add_tours_and_travels','customer_id','leaving_from_id','nationality_id',
                leaving_from_name=F('leaving_from__name'),nationality_name=F('nationality__name'),
              customer_name=F('customer__name'),customer_address=F('customer__address'),
                customer_mobile_number=F('customer__mobile_number'),customer_email=F('customer__email'),
            ).first()
            city_nights=CityNight.objects.filter(package_id=package_id)
            package['city_nights']=serializers.CityNightSerializer(instance=city_nights,many=True,).data
            itineraty=Itinerary.objects.filter(package_id=package_id).order_by('days')
            itineraty_serializer=serializers.ItinerarySerializer(instance=itineraty,many=True)
            
            travel_details=Travel_Details.objects.filter(package_id=package_id).values(
                'destination','id','PNR','road_transport_id','pickup_from',
                vehicle_type=F('road_transport__vehicle_type'),seats=F('road_transport__seats'),
               
                destination_name=F('destination__name'),
                cost=F('road_transport__cost'),
              
                pickup_from_name=F('pickup_from__name'),

            )
            flights_details=Flight_Details.objects.filter(package_id=package_id).values('id',
                'destination_to','ret_destination_to','pickup_from','ret_pickup_from','depart_on','return_on','flt_class','PNR','airlines','type','sequence',
                destination_to_name=F('destination_to__name'),
                ret_destination_to_name=F('ret_destination_to__name'),
                pickup_from_name=F('pickup_from__name'),
                ret_pickup_from_name=F('ret_pickup_from__name'),

            ).order_by('sequence')
            context={
                
                "hoteldetails":hoteldetails,
                "travel_details":travel_details,
                "itineraty":itineraty_serializer.data,
                'flights_details':flights_details
                
            }
            package.update(context)
        
            return Response(package)

        else:    
            req_user = request.user
            if req_user.role == 'Employee':
                company = Employee.objects.filter(emp_user=req_user).first().company
            elif req_user.role == 'Company':
                company = Company.objects.filter(custom_user_id=req_user.id).first()

            packages = CustomisedPackage.objects.filter(company=company).values(
                'id', 'number_of_rooms', 'leaving_on', 'number_of_adults', 'number_of_children',
                'interests', 'who_is_travelling', 'pregnant_women', 'elderly_people', 'with_walking_difficulty',
                'teenager', 'women_only', 'men_only', 'star_rating', 'add_transfers', 'add_tours_and_travels',
                'customer_id', 'leaving_from_id', 'nationality_id', 'updated_at', 'created_at',
                leaving_from_name=F('leaving_from__name'),
                nationality_name=F('nationality__name'),
                customer_name=F('customer__name'),
                customer_address=F('customer__address'),
                customer_mobile_number=F('customer__mobile_number'),
                customer_email=F('customer__email'),
                sent_by=Concat(F('created_by__first_name'), Value(' '), F('created_by__last_name'))
            ).order_by('-created_at')

            # Filtering by date range
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                packages = packages.filter(created_at__range=[start_date, end_date])
    
            # Filtering by customer name or email
            customer_search = request.query_params.get('customer_search')
            if customer_search:
                packages = packages.filter(
                    Q(customer_name__icontains=customer_search) |
                    Q(customer_email__icontains=customer_search)
                )
    
            # Dynamic filter for destination
            destination_search = request.query_params.get('destination')
            if destination_search:
                package_ids = CityNight.objects.filter(city__name__icontains=destination_search).values_list('package_id', flat=True)
                packages = packages.filter(id__in=package_ids)
    
            paginator = self.pagination_class()
            paginated_packages = paginator.paginate_queryset(packages, request, view=self)
    
            for pkg in paginated_packages:
                city_nights = CityNight.objects.filter(package_id=pkg.get('id'))
                if city_nights:
                    city_names = [city_night.city.name for city_night in city_nights]
                    destination = ', '.join(city_names)
    
                    total_nights = city_nights.aggregate(total_nights=Sum('nights'))
                    total_nights_value = total_nights['total_nights'] if total_nights['total_nights'] is not None else 0
    
                    add_on = {
                        "destination": destination,
                        "total_nights": total_nights_value,
                      
                    }
                    pkg.update(add_on)
    
            return paginator.get_paginated_response(paginated_packages)
            # paginator = self.pagination_class()
            # paginated_packages = paginator.paginate_queryset(packages, request, view=self)

            # for pkg in paginated_packages:
            #     city_nights = CityNight.objects.filter(package_id=pkg.get('id'))
            #     if city_nights:
            #         package_name = f"Trip to {city_nights.first().city.name}"
            #         city_names = [city_night.city.name for city_night in city_nights]
            #         destination = ', '.join(city_names)

            #         total_nights = city_nights.aggregate(total_nights=Sum('nights'))
            #         total_nights_value = total_nights['total_nights'] if total_nights['total_nights'] is not None else 0

            #         add_on = {
            #             "destination": destination,
            #             "total_nights": total_nights_value,
            #             "package_name": package_name,
            #         }
            #         pkg.update(add_on)

            # return paginator.get_paginated_response(paginated_packages)

class UpdateCustomisedPackageView(generics.UpdateAPIView):
    queryset=CustomisedPackage.objects.all()
    serializer_class=serializers.CustomisedPackageUpdateSerializer



class RoadTransportListCreateView(BaseListCreateAPIView):
    queryset=RoadTransportOption.objects.all().order_by('seats')
    permission_classes=[AllowAny]
    serializer_class=serializers.RoadTransportSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.RoadTransportSerializer
    filterset_class=RoadTransportFilter
class RoadTransportRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyAPIView):
    queryset=RoadTransportOption.objects.all()
    permission_classes=[AllowAny]
    serializer_class=serializers.RoadTransportSerializer


class HotelListCreateView(BaseListCreateAPIView):
    queryset=Hotel.objects.all()
    permission_classes=[AllowAny]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.HotelSerializer
    filterset_class=HotelsFilter


class HotelRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset=Hotel.objects.all()
    permission_classes=[AllowAny]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.HotelSerializer



# Travel_Details
class TravelDetailsListCreateAPI(BaseListCreateAPIView):
    queryset=Travel_Details.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.TravelDetailsSerializer

class TravelDetailsUpdateDestroyAPI(BaseRetrieveUpdateDestroyAPIView):
    queryset=Travel_Details.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.TravelDetailsSerializer


class InvoiceListCreateAPI(BaseListCreateAPIView):
    queryset=InvoiceMaster.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.InvoiceSerailizer
    search_fields=['invoice_no']
    
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
            return InvoiceMaster.objects.none()

 
class InvoiceUpdateDestroyAPI(BaseRetrieveUpdateDestroyAPIView):
    queryset=InvoiceMaster.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.InvoiceSerailizer
    
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
            return InvoiceMaster.objects.none()

class PaymentReceiptListCreateAPI(BaseListCreateAPIView):
    queryset=PaymentReceipt.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.PaymentReceiptSerializer
    search_fields=['receipt_no']
    
    def get_queryset(self):
        req_user = self.request.user
        if req_user.role == 'Employee':
            if Employee.objects.filter(emp_user=req_user).exists():
                emp = Employee.objects.filter(emp_user=req_user).first()
                return self.queryset.filter(invoice__company=emp.company)
        elif req_user.role == 'Company':
            return self.queryset.filter(invoice__company__custom_user_id=req_user.id)
        elif req_user.role == 'Admin':
            return super().get_queryset()
        else:
            return PaymentReceipt.objects.none()

 
class PaymentReceiptUpdateDestroyAPI(BaseRetrieveUpdateDestroyAPIView):
    queryset=PaymentReceipt.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.PaymentReceiptSerializer
    
    def get_queryset(self):
        req_user = self.request.user
        if req_user.role == 'Employee':
            if Employee.objects.filter(emp_user=req_user).exists():
                emp = Employee.objects.filter(emp_user=req_user).first()
                return self.queryset.filter(invoice__company=emp.company)
        elif req_user.role == 'Company':
            return self.queryset.filter(invoice__company__custom_user_id=req_user.id)
        elif req_user.role == 'Admin':
            return super().get_queryset()
        else:
            return PaymentReceipt.objects.none()
     
class ContactCreateView(generics.CreateAPIView):
    queryset=Contact.objects.all()
    permission_classes=[AllowAny]
    serializer_class=serializers.ContactSerializer
  
class ContactListView(generics.ListAPIView):
    queryset=Contact.objects.all()
    permission_classes=[AllowAny]
    serializer_class=serializers.ContactSerializer

class ContactUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Contact.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class=serializers.ContactSerializer

# Customer
class CustomerListCreateView(BaseListCreateAPIView):
    queryset=Customer.objects.select_related('country', 'state', 'city').all()
    authentication_classes=[JWTAuthentication]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    permission_classes=[IsAuthenticated]
    search_fields=['name','email','mobile_number']
    ordering_fields=['name','email','mobile_number']
    # filterset_fields=['name__icontains','email','mobile_number']
    filterset_class=CustomerFilter
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
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
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
#Expanse 
class ExpanseListCreateView(BaseListCreateAPIView):
    queryset=ExpenseDetail.objects.all()
    authentication_classes=[JWTAuthentication]
    serializer_class=serializers.ExpanseSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields=['vendor']
    permission_classes=[IsAuthenticated]
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
            return ExpenseDetail.objects.none()
        return super().get_queryset()


class ExpanseRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset=ExpenseDetail.objects.all()
    authentication_classes=[JWTAuthentication]
    serializer_class=serializers.ExpanseSerializer
    permission_classes=[IsAuthenticated]


# AirTicketInvoice
class AirTicketInvoiceListCreateView(BaseListCreateAPIView):
    queryset=AirTicketInvoice.objects.all()
    authentication_classes=[JWTAuthentication]
    serializer_class=serializers.AirTicketInvoiceSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields=['invoice_no']
    permission_classes=[IsAuthenticated]
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
            return AirTicketInvoice.objects.none()
        return super().get_queryset()


class AirTicketInvoiceRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset=AirTicketInvoice.objects.all()
    authentication_classes=[JWTAuthentication]
    serializer_class=serializers.AirTicketInvoiceSerializer
    permission_classes=[IsAuthenticated]



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

class CitiesUpdateDestroyView(generics.UpdateAPIView,generics.DestroyAPIView):
    queryset=Cities.objects.all()
    serializer_class=serializers.CitieSerializer

class CitiesListView(generics.ListAPIView):
    queryset=Cities.objects.all()
    serializer_class=serializers.CitieSerializer
    filter_backends=[DjangoFilterBackend, filters.SearchFilter]
    search_fields=['name']
    ordering='name'
    pagination_class=CustomPagination
    

    def get(self, request, *args, **kwargs):
        state_id=self.kwargs.get('state_id')
        search=self.kwargs.get('search')
        pk=self.kwargs.get('pk')
    
        if search:
            queryset = self.queryset.filter(name__istartswith=search,country_id=101).values(
                'id', 'name', 'state_id', 'country_id',
                country_name=F('country__name'),
                state_name=F('state__name')
            )
            print(search)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(page)
        
        elif pk:
            queryset =self.queryset.filter(id=pk).values(
                'id', 'name', 'state_id', 'country_id',
                country_name=F('country__name'),
                state_name=F('state__name')
            )
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(page)
        
       
        elif state_id:
            queryset=self.queryset.filter(state_id=state_id)
            search_query = self.request.query_params.get('search')
            if search_query:
                queryset = queryset.filter(name__icontains=search_query).values('id','name','state_id','country_id',country_name=F('country__name'),state_name=F('state__name'),)
                return Response(queryset)


            return Response(queryset.values('id','name','state_id','country_id',country_name=F('country__name'),state_name=F('state__name'),), status=status.HTTP_200_OK)

        else:
            queryset = self.queryset.filter(country_id=101).values(
                'id', 'name', 'state_id', 'country_id',
                country_name=F('country__name'),
                state_name=F('state__name')
            )
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(page)

class FlightsDataApi(APIView):
    def post(self, request, *args, **kwargs):
      try:
          serializer= serializers.FlightsDataSerializer(data=request.data)
          if serializer.is_valid(raise_exception=True):
              data=serializer.validated_data
              to_city_data=data.get('to_city')
              from_city_data=data.get('from_city')
              departure_dateobj=data.get('departure_date')
              departure_date=departure_dateobj.strftime('%a, %b %d')
              print(to_city_data,from_city_data,departure_date)
              # Set up Chrome options if needed (e.g., headless mode, specific settings)
             
              url = "https://www.google.com/travel/flights?tfs=CBwQARoPag0IAhIJL20vMDFkODhjQAFIAXABggELCP___________wGYAQI&tfu=KgIIAw"
              driver.get(url)



              from_city = WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.XPATH, '//*[@id="i23"]/div[1]/div/div/div[1]/div/div/input[@aria-label="Where from?"]'))
              )

              from_city.clear()
              from_city.send_keys(from_city_data)
              time.sleep(1)
              select_from_city=driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]')
              select_from_city.click()

              # Wait for the "To" input field to be present and find it uniquely by its placeholder text
              to_city = WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.XPATH, '//*[@id="i23"]/div[4]/div/div/div[1]/div/div/input[@aria-label="Where to? "]'))
              )
              to_city.clear()
              to_city.send_keys(to_city_data)
              time.sleep(1)
              select_to_city=driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]')
              select_to_city.click()

              # Wait for some time to see the results (optional)
              time.sleep(1)

              # select date
              select_departure_date=driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input[@aria-label="Departure"]')
              select_departure_date.send_keys(departure_date)
              select_departure_date.click()
              time.sleep(2)

              done_btn=driver.find_element(By.XPATH,'//*[@id="ow79"]/div[2]/div/div[3]/div[3]/div/button[1]')
              done_btn.click()

              searchbtn=driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button[@aria-label="Search"]') 
              searchbtn.click()
              time.sleep(2)

              # best_flights= driver.find_elements(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul')
              page_source = driver.page_source
              soup = BeautifulSoup(page_source, 'html.parser')
              flights=soup.find_all('ul',class_='Rk10dc')
              # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
              #         # Build the absolute path to the countries.json file
              # file_path = os.path.join(base_dir,'travelling-erp', 'flights.html')
              # with open(file_path, encoding='utf-8', mode='w+') as f:
              #     f.write(str(flights))
              count=0
              flights_data = []
              for flgt in flights:
                  for flgt_li in flgt.find_all('li')[:-1]:
                      count+=1
                      # print(count)

                      from_depart=flgt_li.find(class_='G2WY5c sSHqwe ogfYpf tPgKwe').text
                      to=flgt_li.find(class_='c8rWCd sSHqwe ogfYpf tPgKwe').text
                      dep_time=flgt_li.find(class_='wtdjmc YMlIz ogfYpf tPgKwe').text
                      avi_time=flgt_li.find(class_='XWcVob YMlIz ogfYpf tPgKwe').text
                      stops=flgt_li.find(class_='VG3hNb').text
                      airline=flgt_li.find(class_='h1fkLb').text
                      price_div = flgt_li.find(class_='YMlIz FpEdX')
                      price = price_div.find('span').text if price_div else "N/A"
                      img_div = flgt_li.find(class_='EbY4Pc P2UJoe')
                      if img_div:
                          style = img_div.get('style')
                          # Extract the URL from the style attribute using a regular expression
                          img_url_match = re.search(r'url\((.*?)\)', style)
                          img_url = img_url_match.group(1) if img_url_match else None
                      duration = flgt_li.find(class_='gvkrdb AdWm1c tPgKwe ogfYpf').text
                      flight_info = {
                          "from_depart": from_depart,
                          "to": to,
                          "dep_time": dep_time,
                          "avi_time": avi_time,
                          "stops": stops,
                          "airline": airline,
                          "price": price,
                          "img_url": img_url,
                          "duration": duration
                      }

                      flights_data.append(flight_info)
              print(flights_data)
              return Response(flights_data)
      except ValidationError as e:
        return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
          
          print(e)
          return Response({"error":e})


@api_view(['GET'])
@permission_classes([AllowAny])
def activity_data_entry(request):
    try:
        cities_data = {
    'Udaipur': {
       
        'activities': [
            {'name': 'City Palace Tour', 'category': 'history', 'duration': '2 hours', 'age_limit': 12, 'desc': 'Explore the historic City Palace.'},
            {'name': 'Lake Pichola Boat Ride', 'category': 'leisure', 'duration': '1 hour', 'age_limit': 5, 'desc': 'Enjoy a serene boat ride on Lake Pichola.'},
            {'name': 'Jag Mandir Visit', 'category': 'honeymoon', 'duration': '3 hours', 'age_limit': None, 'desc': 'Visit the beautiful Jag Mandir island palace.'},
            {'name': 'Saheliyon Ki Bari', 'category': 'art_and_culture', 'duration': '1.5 hours', 'age_limit': None, 'desc': 'Stroll through the historic garden of Saheliyon Ki Bari.'},
            {'name': 'Bagore Ki Haveli', 'category': 'art_and_culture', 'duration': '2 hours', 'age_limit': None, 'desc': 'Discover the cultural heritage of Bagore Ki Haveli.'},
            {'name': 'Fateh Sagar Lake', 'category': 'leisure', 'duration': '2 hours', 'age_limit': None, 'desc': 'Relax by the scenic Fateh Sagar Lake.'},
            {'name': 'Eklingji Temple Visit', 'category': 'history', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the ancient Eklingji Temple.'},
            {'name': 'Monsoon Palace Visit', 'category': 'adventure', 'duration': '2 hours', 'age_limit': 10, 'desc': 'Hike up to the Monsoon Palace for stunning views.'},
            {'name': 'Shilpgram Visit', 'category': 'shopping', 'duration': '3 hours', 'age_limit': None, 'desc': 'Shop for traditional crafts at Shilpgram.'},
            {'name': 'Ambrai Ghat', 'category': 'nightlife', 'duration': '1 hour', 'age_limit': 18, 'desc': 'Enjoy the nightlife at Ambrai Ghat.'},
        ]
    },
    'Jaipur': {
      
        'activities': [
            {'name': 'Amber Fort Tour', 'category': 'history', 'duration': '3 hours', 'age_limit': None, 'desc': 'Tour the magnificent Amber Fort.'},
            {'name': 'Hawa Mahal Visit', 'category': 'art_and_culture', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the iconic Hawa Mahal.'},
            {'name': 'City Palace Jaipur', 'category': 'history', 'duration': '2 hours', 'age_limit': None, 'desc': 'Explore the historic City Palace of Jaipur.'},
            {'name': 'Jantar Mantar', 'category': 'art_and_culture', 'duration': '1.5 hours', 'age_limit': None, 'desc': 'Discover the astronomical instruments at Jantar Mantar.'},
            {'name': 'Jaipur Zoo Visit', 'category': 'entertainment', 'duration': '2 hours', 'age_limit': None, 'desc': 'Visit the Jaipur Zoo and see various animals.'},
            {'name': 'Jal Mahal Visit', 'category': 'honeymoon', 'duration': '1 hour', 'age_limit': None, 'desc': 'Admire the Jal Mahal palace in the middle of Man Sagar Lake.'},
            {'name': 'Albert Hall Museum', 'category': 'history', 'duration': '1.5 hours', 'age_limit': None, 'desc': 'Explore the exhibits at the Albert Hall Museum.'},
            {'name': 'Nahargarh Fort Visit', 'category': 'adventure', 'duration': '3 hours', 'age_limit': None, 'desc': 'Hike up to Nahargarh Fort for panoramic views of Jaipur.'},
            {'name': 'Bapu Bazaar Shopping', 'category': 'shopping', 'duration': '2 hours', 'age_limit': None, 'desc': 'Shop for souvenirs at Bapu Bazaar.'},
            {'name': 'Chokhi Dhani', 'category': 'nightlife', 'duration': '4 hours', 'age_limit': None, 'desc': 'Experience Rajasthani culture at Chokhi Dhani.'},
        ]
    },
    'Manali': {
 
        'activities': [
            {'name': 'Rohtang Pass', 'category': 'adventure', 'duration': '5 hours', 'age_limit': None, 'desc': 'Experience the thrill of visiting Rohtang Pass.'},
            {'name': 'Solang Valley', 'category': 'adventure', 'duration': '4 hours', 'age_limit': 10, 'desc': 'Enjoy adventure sports in Solang Valley.'},
            {'name': 'Hadimba Temple', 'category': 'history', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the ancient Hadimba Temple.'},
            {'name': 'Old Manali', 'category': 'art_and_culture', 'duration': '2 hours', 'age_limit': None, 'desc': 'Explore the quaint village of Old Manali.'},
            {'name': 'Vashisht Hot Water Springs', 'category': 'spa', 'duration': '1 hour', 'age_limit': None, 'desc': 'Relax at the Vashisht Hot Water Springs.'},
            {'name': 'Manu Temple', 'category': 'history', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the Manu Temple, dedicated to sage Manu.'},
            {'name': 'Jogini Waterfall', 'category': 'adventure', 'duration': '3 hours', 'age_limit': None, 'desc': 'Hike to the beautiful Jogini Waterfall.'},
            {'name': 'Tibetan Monastery', 'category': 'art_and_culture', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the Tibetan Monastery and explore Tibetan culture.'},
            {'name': 'Mall Road Shopping', 'category': 'shopping', 'duration': '2 hours', 'age_limit': None, 'desc': 'Shop for souvenirs on Mall Road.'},
            {'name': 'Manali Sanctuary', 'category': 'leisure', 'duration': '3 hours', 'age_limit': None, 'desc': 'Explore the natural beauty of Manali Sanctuary.'},
        ]
    },
    'Mumbai': {
                'activities': [
                    {'name': 'Gateway of India', 'category': 'history', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the iconic Gateway of India.'},
                    {'name': 'Marine Drive', 'category': 'leisure', 'duration': '2 hours', 'age_limit': None, 'desc': 'Enjoy a leisurely walk along Marine Drive.'},
                    {'name': 'Elephanta Caves', 'category': 'history', 'duration': '3 hours', 'age_limit': None, 'desc': 'Explore the ancient Elephanta Caves.'},
                    {'name': 'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya', 'category': 'art_and_culture', 'duration': '2 hours', 'age_limit': None, 'desc': 'Visit the museum to learn about Mumbai\'s history.'},
                    {'name': 'Juhu Beach', 'category': 'leisure', 'duration': '2 hours', 'age_limit': None, 'desc': 'Relax at Juhu Beach and enjoy local snacks.'},
                    {'name': 'Siddhivinayak Temple', 'category': 'spiritual', 'duration': '1 hour', 'age_limit': None, 'desc': 'Seek blessings at the Siddhivinayak Temple.'},
                    {'name': 'Colaba Causeway', 'category': 'shopping', 'duration': '2 hours', 'age_limit': None, 'desc': 'Shop for unique items at Colaba Causeway.'},
                    {'name': 'Haji Ali Dargah', 'category': 'spiritual', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the Haji Ali Dargah located on an islet.'},
                    {'name': 'Sanjay Gandhi National Park', 'category': 'adventure', 'duration': '4 hours', 'age_limit': None, 'desc': 'Explore the wildlife and nature at Sanjay Gandhi National Park.'},
                    {'name': 'Bandra-Worli Sea Link', 'category': 'leisure', 'duration': '30 mins', 'age_limit': None, 'desc': 'Drive over the stunning Bandra-Worli Sea Link.'},
                ]
            },
    'Delhi': {
                'activities': [
                    {'name': 'Red Fort', 'category': 'history', 'duration': '2 hours', 'age_limit': None, 'desc': 'Explore the historic Red Fort.'},
                    {'name': 'Qutub Minar', 'category': 'history', 'duration': '1.5 hours', 'age_limit': None, 'desc': 'Visit the tallest brick minaret in the world.'},
                    {'name': 'India Gate', 'category': 'history', 'duration': '1 hour', 'age_limit': None, 'desc': 'Pay your respects at India Gate.'},
                    {'name': 'Lotus Temple', 'category': 'spiritual', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the beautiful Lotus Temple.'},
                    {'name': 'Humayun\'s Tomb', 'category': 'history', 'duration': '1.5 hours', 'age_limit': None, 'desc': 'Explore Humayun\'s Tomb, a UNESCO World Heritage site.'},
                    {'name': 'Chandni Chowk', 'category': 'shopping', 'duration': '3 hours', 'age_limit': None, 'desc': 'Shop for various goods in the bustling Chandni Chowk market.'},
                    {'name': 'Akshardham Temple', 'category': 'spiritual', 'duration': '3 hours', 'age_limit': None, 'desc': 'Visit the magnificent Akshardham Temple.'},
                    {'name': 'Jama Masjid', 'category': 'spiritual', 'duration': '1 hour', 'age_limit': None, 'desc': 'Visit the grand Jama Masjid mosque.'},
                    {'name': 'Raj Ghat', 'category': 'history', 'duration': '1 hour', 'age_limit': None, 'desc': 'Pay homage at the memorial of Mahatma Gandhi.'},
                    {'name': 'Lodhi Gardens', 'category': 'leisure', 'duration': '2 hours', 'age_limit': None, 'desc': 'Relax and enjoy nature at Lodhi Gardens.'},
                ]
            },
            
  "Agra": {
    "activities": [
      {
        "name": "Taj Mahal Visit",
        "category": "Historical",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Explore the iconic symbol of love, one of the Seven Wonders of the World."
      },
      {
        "name": "Agra Fort Tour",
        "category": "Historical",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Discover the grand Mughal architecture and rich history of Agra Fort."
      },
      {
        "name": "Fatehpur Sikri Excursion",
        "category": "Historical",
        "duration": "4 hours",
        "age_limit": "All ages",
        "desc": "Visit the abandoned Mughal city, a UNESCO World Heritage site."
      },
      {
        "name": "Mohabbat the Taj Show",
        "category": "Entertainment",
        "duration": "2 hours",
        "age_limit": "5+",
        "desc": "Watch a spectacular live performance depicting the love story behind the Taj Mahal."
      }
    ]
  },
  "Varanasi": {
    "activities": [
      {
        "name": "Sunrise Boat Ride on Ganges",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Witness the spiritual awakening of the holy city with a serene boat ride at dawn."
      },
      {
        "name": "Evening Ganga Aarti",
        "category": "Religious",
        "duration": "1 hour",
        "age_limit": "All ages",
        "desc": "Experience the mesmerizing ritual of light and sound on the banks of the Ganges."
      },
      {
        "name": "Sarnath Excursion",
        "category": "Historical",
        "duration": "4 hours",
        "age_limit": "All ages",
        "desc": "Visit the site where Buddha gave his first sermon after enlightenment."
      },
      {
        "name": "Varanasi Food Walk",
        "category": "Culinary",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Sample local delicacies and street food in the narrow lanes of Varanasi."
      }
    ]
  },
  "Amritsar": {
    "activities": [
      {
        "name": "Golden Temple Langar Experience",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Participate in the world's largest free community kitchen at the Golden Temple."
      },
      {
        "name": "Wagah Border Ceremony",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Witness the patriotic flag-lowering ceremony at the India-Pakistan border."
      },
      {
        "name": "Punjabi Cooking Class",
        "category": "Culinary",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Learn to prepare authentic Punjabi dishes from local chefs."
      },
      {
        "name": "Maharaja Ranjit Singh Panorama",
        "category": "Historical",
        "duration": "1.5 hours",
        "age_limit": "All ages",
        "desc": "Experience a 360-degree depiction of the life and times of Maharaja Ranjit Singh."
      }
    ]
  },
  "Kolkata": {
    "activities": [
      {
        "name": "Tram Ride",
        "category": "Leisure",
        "duration": "1 hour",
        "age_limit": "All ages",
        "desc": "Take a nostalgic ride on Kolkata's historic tram system, one of the oldest in Asia."
      },
      {
        "name": "Bengali Cooking Class",
        "category": "Culinary",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Learn to prepare authentic Bengali dishes from expert local chefs."
      },
      {
        "name": "Sundarbans Day Trip",
        "category": "Nature",
        "duration": "12 hours",
        "age_limit": "8+",
        "desc": "Explore the world's largest mangrove forest and spot Royal Bengal tigers."
      },
      {
        "name": "Kumartuli Pottery Village Tour",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Visit the traditional potters' quarter and see artisans creating clay idols."
      }
    ]
  },
  "Panaji": {
    "activities": [
      {
        "name": "Cruise on Mandovi River",
        "category": "Leisure",
        "duration": "1 hour",
        "age_limit": "All ages",
        "desc": "Enjoy a relaxing cruise with live music and stunning views of Panaji's coastline."
      },
      {
        "name": "Spice Plantation Tour",
        "category": "Educational",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Explore a fragrant spice plantation and learn about Goa's spice trading history."
      },
      {
        "name": "Old Goa Churches Tour",
        "category": "Historical",
        "duration": "4 hours",
        "age_limit": "All ages",
        "desc": "Visit the UNESCO World Heritage churches of Old Goa, including Basilica of Bom Jesus."
      },
      {
        "name": "Fontainhas Heritage Walk",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Explore the charming Latin Quarter of Panaji with its colorful Portuguese-era houses."
      }
    ]
  },
  "Rishikesh": {
    "activities": [
      {
        "name": "White Water Rafting",
        "category": "Adventure",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Experience thrilling rapids on the Ganges River with experienced guides."
      },
      {
        "name": "Yoga and Meditation Session",
        "category": "Wellness",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Participate in a traditional yoga and meditation class in the yoga capital of the world."
      },
      {
        "name": "Bungee Jumping",
        "category": "Adventure",
        "duration": "30 minutes",
        "age_limit": "14+",
        "desc": "Take a leap from India's highest bungee jumping platform (83 meters)."
      },
      {
        "name": "Beatles Ashram Visit",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Explore the abandoned ashram where The Beatles stayed and composed many songs."
      }
    ]
  }

,
  "Mysuru": {
    "activities": [
      {
        "name": "Mysore Palace Light Show",
        "category": "Entertainment",
        "duration": "1 hour",
        "age_limit": "All ages",
        "desc": "Witness the grand Mysore Palace illuminated by thousands of lights in the evening."
      },
      {
        "name": "Ashtanga Yoga Class",
        "category": "Wellness",
        "duration": "2 hours",
        "age_limit": "16+",
        "desc": "Practice the traditional Ashtanga Yoga in its birthplace with experienced instructors."
      },
      {
        "name": "Silk Weaving Workshop",
        "category": "Cultural",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Learn the art of silk weaving and create your own silk product to take home."
      },
      {
        "name": "Chamundi Hill Trek",
        "category": "Adventure",
        "duration": "4 hours",
        "age_limit": "10+",
        "desc": "Climb 1000 steps to reach the Chamundeshwari Temple for panoramic views of Mysore."
      }
    ]
  },
  "Cochin": {
    "activities": [
      {
        "name": "Kerala Backwaters Houseboat Cruise",
        "category": "Leisure",
        "duration": "8 hours",
        "age_limit": "All ages",
        "desc": "Enjoy a serene cruise through the backwaters on a traditional Kerala houseboat."
      },
      {
        "name": "Kathakali Performance",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Watch a mesmerizing performance of Kerala's traditional dance-drama."
      },
      {
        "name": "Fort Kochi Cycling Tour",
        "category": "Adventure",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Explore the historic Fort Kochi area on a bicycle, visiting key attractions."
      },
      {
        "name": "Kochi Fishing Net Experience",
        "category": "Cultural",
        "duration": "1 hour",
        "age_limit": "12+",
        "desc": "Try your hand at operating the famous Chinese fishing nets of Kochi."
      }
    ]
  },
  "Shimla": {
    "activities": [
      {
        "name": "Toy Train Ride",
        "category": "Leisure",
        "duration": "5 hours",
        "age_limit": "All ages",
        "desc": "Enjoy a scenic journey on the UNESCO World Heritage Kalka-Shimla Railway."
      },
      {
        "name": "Ice Skating",
        "category": "Adventure",
        "duration": "2 hours",
        "age_limit": "6+",
        "desc": "Visit Asia's only natural ice skating rink (seasonal - winter months only)."
      },
      {
        "name": "Mall Road Shopping",
        "category": "Leisure",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Stroll along the famous Mall Road, shopping for local handicrafts and souvenirs."
      },
      {
        "name": "Jakhu Temple Trek",
        "category": "Adventure",
        "duration": "4 hours",
        "age_limit": "10+",
        "desc": "Hike to the famous Hanuman temple at the highest point in Shimla."
      }
    ]
  },
  "Hyderabad": {
    "activities": [
      {
        "name": "Charminar Night Bazaar",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Explore the bustling night market around the iconic Charminar monument."
      },
      {
        "name": "Biryani Cooking Class",
        "category": "Culinary",
        "duration": "3 hours",
        "age_limit": "14+",
        "desc": "Learn to cook the famous Hyderabadi Biryani from expert local chefs."
      },
      {
        "name": "Ramoji Film City Tour",
        "category": "Entertainment",
        "duration": "8 hours",
        "age_limit": "All ages",
        "desc": "Visit the world's largest film studio complex and enjoy various attractions."
      },
      {
        "name": "Hussain Sagar Lake Boating",
        "category": "Leisure",
        "duration": "1 hour",
        "age_limit": "All ages",
        "desc": "Take a boat ride on Hussain Sagar Lake and visit the Buddha statue in the middle."
      }
    ]
  },
  "Darjeeling": {
    "activities": [
      {
        "name": "Tiger Hill Sunrise View",
        "category": "Nature",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Witness a spectacular sunrise over the Kanchenjunga mountain range."
      },
      {
        "name": "Tea Estate Tour",
        "category": "Educational",
        "duration": "4 hours",
        "age_limit": "All ages",
        "desc": "Visit a tea plantation, learn about tea processing, and enjoy a tea tasting session."
      },
      {
        "name": "Darjeeling Himalayan Railway Ride",
        "category": "Leisure",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Take a joy ride on the UNESCO World Heritage 'Toy Train'."
      },
      {
        "name": "Rock Climbing at Tenzing Rock",
        "category": "Adventure",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Try rock climbing and rappelling at the famous Tenzing Rock."
      }
    ]
  },
  "Puducherry": {
    "activities": [
      {
        "name": "Auroville Visit",
        "category": "Cultural",
        "duration": "4 hours",
        "age_limit": "All ages",
        "desc": "Explore the experimental township of Auroville and visit the Matrimandir."
      },
      {
        "name": "French Quarter Walking Tour",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Stroll through the charming French Quarter with its colonial architecture."
      },
      {
        "name": "Scuba Diving",
        "category": "Adventure",
        "duration": "4 hours",
        "age_limit": "10+",
        "desc": "Discover the underwater world of the Bay of Bengal with a scuba diving session."
      },
      {
        "name": "Seaside Promenade Cycling",
        "category": "Leisure",
        "duration": "2 hours",
        "age_limit": "8+",
        "desc": "Cycle along the beautiful seaside promenade, enjoying the sea breeze."
      }
    ]
  },
  "Ahmedabad": {
    "activities": [
      {
        "name": "Heritage Walk",
        "category": "Cultural",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Explore the old city's pol architecture and hidden cultural gems."
      },
      {
        "name": "Kite Flying Experience",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "6+",
        "desc": "Learn and enjoy the art of kite flying, especially during the Uttarayan festival."
      },
      {
        "name": "Sabarmati Ashram Visit",
        "category": "Historical",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Visit Mahatma Gandhi's former residence and learn about India's independence movement."
      },
      {
        "name": "Textile Museum Tour",
        "category": "Educational",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Explore the rich textile heritage of Gujarat at the Calico Museum of Textiles."
      }
    ]
  },
  "Jodhpur": {
    "activities": [
      {
        "name": "Mehrangarh Fort Audio Tour",
        "category": "Historical",
        "duration": "3 hours",
        "age_limit": "All ages",
        "desc": "Explore the majestic Mehrangarh Fort with an immersive audio guide."
      },
      {
        "name": "Zip-lining over Jodhpur",
        "category": "Adventure",
        "duration": "2 hours",
        "age_limit": "10+",
        "desc": "Experience thrilling zip-lines offering panoramic views of the Blue City."
      },
      {
        "name": "Desert Camping and Camel Safari",
        "category": "Adventure",
        "duration": "24 hours",
        "age_limit": "All ages",
        "desc": "Enjoy a camel ride in the Thar Desert and camp under the stars."
      },
      {
        "name": "Blue City Walking Tour",
        "category": "Cultural",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Explore the narrow lanes of the old city, famous for its blue-painted houses."
      }
    ]
  },
  "Aurangabad": {
    "activities": [
      {
        "name": "Ajanta Caves Excursion",
        "category": "Historical",
        "duration": "8 hours",
        "age_limit": "All ages",
        "desc": "Visit the UNESCO World Heritage Ajanta Caves, known for Buddhist rock-cut cave monuments."
      },
      {
        "name": "Ellora Caves Tour",
        "category": "Historical",
        "duration": "6 hours",
        "age_limit": "All ages",
        "desc": "Explore the Ellora Caves, showcasing Hindu, Buddhist, and Jain monuments."
      },
      {
        "name": "Bibi Ka Maqbara Visit",
        "category": "Historical",
        "duration": "2 hours",
        "age_limit": "All ages",
        "desc": "Visit the 'Taj of the Deccan', a beautiful mausoleum similar to the Taj Mahal."
      },
      {
        "name": "Paithani Saree Weaving Workshop",
        "category": "Cultural",
        "duration": "3 hours",
        "age_limit": "12+",
        "desc": "Learn about the intricate art of weaving Paithani sarees, famous in Maharashtra."
      }
    ]
  }

}

        # Generate cities and activities
        for city_name, city_data in cities_data.items():
            city = Cities.objects.filter(
                name=city_name, 
            ).first()
            print(city)
            for i, activity_data in enumerate(city_data['activities']):
                print(Activity.objects.filter(activity_name=activity_data['name'],activity_city__name=city.name).exists())
                if  not Activity.objects.filter(activity_name=activity_data['name'],activity_city__name=city.name).exists():
                    activity = Activity.objects.create(
                    category=[activity_data['category']],
                    duration=activity_data['duration'],
                    age_limit=activity_data['age_limit'] ,
                    activity_name=activity_data['name'],
                    sequence=i + 1,
                    activity_desc=activity_data['desc'],
                    activity_city_id=city.id
                )
                    print(f"Created activity: {activity.activity_name} in {city.name}")
                else:
                    print(f"Already created activity {activity_data['name']}-{city_name}  ")
        return Response({"message": "Success creating activity"})
    except Exception as e:
        return Response({"error": str(e)})
            

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
                # if country_data['name']=="India":
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
                # if not States.objects.filter(name=states_data['name'],country_id=states_data.get('country_id'),).exists():
                if states_data.get('country_id')==101:
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
                # if not Cities.objects.filter(name=city_data['name'],country_id=city_data.get('country_id'),state=city_data.get('state_id')).exists():
                if city_data.get('country_id')==101:
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



@api_view(['GET'])
@permission_classes([AllowAny])
@transaction.atomic()
def rt_data_entry(request):
    try:
        # Get the current directory of this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Build the absolute path to the countries.json file
        json_file_path = os.path.join(base_dir, 'data', 'road_transport.json')

        

        with open(json_file_path.replace('\\\\','\\'), encoding='utf-8') as f:
            rt_list = json.load(f)['rt']
        
            for rt in rt_list:
                if not RoadTransportOption.objects.filter(vehicle_type=rt.get('vehicle_type'),destination__name__contains=rt.get('destination'),pickup_from__name__contains=rt.get('pickup_from'),seats=rt.get('seats')):
                    print(rt.get('pickup_from'))
                    rt['destination']=Cities.objects.filter(name__contains=rt.get('destination')).first()
                    rt['pickup_from']=Cities.objects.filter(name__contains=rt.get('pickup_from')).first()
                    print(rt.get('destination'),rt.get('pickup_from'))
                    if rt.get('destination') and rt.get('pickup_from') :
                        rt_obj= RoadTransportOption.objects.create(**rt)
                        print("Added ",rt_obj)
                else:
                    print("already exists")
        return Response({'status': 'success', 'message': 'transport data entry completed successfully.'})
    
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
@transaction.atomic()
def hotel_data_entry(request):
    try:
        # Get the current directory of this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Build the absolute path to the countries.json file
        json_file_path = os.path.join(base_dir, 'data', 'hotel.json')
        # Open and load the JSON file

        with open(json_file_path.replace('\\\\','\\'), encoding='utf-8') as f:
            hotels_list = json.load(f)['hotels']
            for hotels in hotels_list:
                city_name=hotels.get('srchO').get('cnm')
                city_obj=Cities.objects.filter(name=city_name).first()
                # print(city_name,city_obj)
                resorts=hotels.get('rsltA')
                for resort in resorts:
                    # print(resort,end="\n\n")
                    area=resort.get('area')
                    address=resort.get('loc')
                    image_url=resort.get('img')
                    roomtype=resort.get('rnm')
                    name=resort.get('nm')
                    star=resort.get('st')
                    rate=resort.get('urtO').get('rt') if resort.get('urtO') else None
                    numRt=resort.get('urtO').get('numRt') if resort.get('urtO') else None
                    price=resort.get('pr')
                    meal_plan=resort.get('mpN')
                    ln=resort.get('ln') if resort.get('ln') else None
                    lt=resort.get('lt') if resort.get('lt') else None
                    if not Hotel.objects.filter(name=name,city_id=city_obj.id).exists():
                        hotel=Hotel.objects.create(
                                name=name,
                                address=address,
                                area=area,
                                city=city_obj,
                                star_rating=star,
                                rate=rate,
                                image_url=image_url,
                                ln=ln,
                                lt=lt
                        )

                        if hotel:
                            RoomType.objects.create(hotel=hotel,rnm=roomtype,meal_plan=meal_plan,
                                                price=price)
                        print(hotel)
                    else:
                        print(F"{name} is already exists in database.")
            return Response({'status': 'success', 'message': 'Hotel data entry completed successfully.'})
    
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)
