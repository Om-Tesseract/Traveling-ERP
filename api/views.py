import datetime
import json
import os
from django.db import transaction
from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.views import APIView
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


#dashboard view
class DashboardListView(APIView):
        
    def get(self,request,*args, **kwargs):
        req_user = self.request.user
        company=None
        if req_user.role == 'Employee':
            if Employee.objects.filter(emp_user=req_user).exists():
                company = Employee.objects.filter(emp_user=req_user).first().company
                
        elif req_user.role == 'Company':
            company= Company.objects.filter(company__custom_user_id=req_user.id)
        if company is not None:
            total_customer= Customer.objects.filter(company=company).count()
            total_pending_itinerary= Itinerary.objects.filter(package__company=company,status="PENDING").count()
            total_completed_itinerary= Itinerary.objects.filter(package__company=company,status="COMPLETED").count()
            context={
                "total_customers": total_customer,
                "total_pending_itinerary":total_pending_itinerary,
                "total_completed_itinerary":total_completed_itinerary

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
    queryset=Activity.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.ActivitySerializer
    search_fields=['activity_name','activity_city__name']
    pagination_class=CustomPagination
    filterset_class=ActivityFilter
    ordering='sequence'

class ActivityUpdateDestroyAPI(BaseRetrieveUpdateDestroyAPIView):
    queryset=Activity.objects.all()
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    serializer_class=serializers.ActivitySerializer



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
                'id','hotel',
                'check_in_date','check_out_date','room_type','number_of_rooms',
                'total_price','additional_requests',
                hotel_name=F('hotel__name'),hotel_address=F('hotel__address'),
                hotel_city=F('hotel__city'),hotel_state=F('hotel__city__state__name'),
                hotel_country=F('hotel__city__country__name'),
                hotel_city_name=F('hotel__city__name'),hotel_star_rating=F('hotel__star_rating'),
                image_url=F('hotel__image_url'),ln=F('hotel__ln'),lt=F('hotel__lt'),
                contact_info=F('hotel__contact_info'),
                review_rate=F('hotel__rate')
            )
            for ht in hoteldetails:
                room_types=RoomType.objects.filter(hotel_id=ht.get('hotel'))
                ht['meal_plan']=room_types.filter(rnm=ht.get('room_type')).first().meal_plan if room_types.filter(rnm=ht.get('room_type')).first() else None
                # ht['amenity']=json.load(room_types.filter(rnm=ht.get('room_type')).first().amenity) if room_types.filter(rnm=ht.get('room_type')).first() else None
                try:
                    if room_types.filter(rnm=ht.get('room_type')).first().amenity:
                        amenity_list = json.loads(room_types.filter(rnm=ht.get('room_type')).first().amenity)
                        ht['amenity'] = amenity_list
                except json.JSONDecodeError as e:
                    # Handle JSON decoding error
                    print(f"Error decoding JSON: {e}")
                    ht['amenity'] = None
                except AttributeError as e:
                    # Handle attribute error if the filter or first() fails
                    print(f"Attribute error: {e}")
                    ht['amenity'] = None
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
            flights_details=Flight_Details.objects.filter(package_id=package_id).values(
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
    queryset=RoadTransportOption.objects.all()
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
}

        # Generate cities and activities
        for city_name, city_data in cities_data.items():
            city = Cities.objects.filter(
                name=city_name, 
            ).first()
            # print(city)
            for i, activity_data in enumerate(city_data['activities']):
                print(Activity.objects.filter(activity_name=activity_data['name'],activity_city__name=city.name).exists())
                if  not Activity.objects.filter(activity_name=activity_data['name'],activity_city__name=city.name).exists():
                    activity = Activity.objects.create(
                    category=[activity_data['category']],
                    duration=activity_data['duration'],
                    age_limit=activity_data['age_limit'],
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
