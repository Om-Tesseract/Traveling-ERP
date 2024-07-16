
# serializers.py
import datetime
import json
from rest_framework import serializers
from api.models import *
from itertools import cycle
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(slug_field='name', queryset=Country.objects.all())
    state = serializers.SlugRelatedField(slug_field='name', queryset=States.objects.all())
    city = serializers.SlugRelatedField(slug_field='name', queryset=Cities.objects.all())

    class Meta:
        model = Customer
        fields = '__all__'

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['country'] = instance.country.name if instance.country else None
        data['country_id'] = instance.country.id if instance.country else None
        data['state'] = instance.state.name if instance.state else None
        data['state_id'] = instance.state.id if instance.state else None
        data['city'] = instance.city.name if instance.city else None
        data['city_id'] = instance.city.id if instance.city else None
        return data
    def create(self, validated_data):
        req_user=self.context.get('request').user
        if req_user.role == 'Employee':
            company = Employee.objects.filter(emp_user=req_user).first().company
            validated_data['company']=company
        
        elif req_user.role == 'Company':
            # print(req_user.email)
            company = Company.objects.filter(custom_user_id=req_user.id).first()
            # print("company==>",company)
            validated_data['company'] = company
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        req_user = self.context.get('request').user
        if req_user.role == 'Employee':
            company = Employee.objects.filter(emp_user=req_user).first().company
            validated_data['company'] = company
        elif req_user.role == 'Company':
            company = Company.objects.filter(custom_user_id=req_user.id).first()
            validated_data['company'] = company
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    emp_first_name=serializers.CharField(write_only=True,)
    emp_nick_name=serializers.CharField(write_only=True,allow_null=True,required=False,allow_blank=True)
    emp_last_name=serializers.CharField(write_only=True)
    emp_mobile_number=serializers.CharField(write_only=True)
    emp_address1=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    emp_address2=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    emp_email=serializers.EmailField(write_only=True)
    emp_password=serializers.CharField(write_only=True)
    emp_dob=serializers.DateField(write_only=True,allow_null=True,required=False)


    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs ={
            "emp_name":{
                "required":False,
            },
            "emp_password":{
                "required":False,
            }
        }

    def to_representation(self, instance:Employee):
        data=super().to_representation(instance)
        data['emp_dob']=instance.emp_dob
        if instance.emp_user:
            data['emp_first_name'] = instance.emp_user.first_name
            data['emp_last_name'] = instance.emp_user.last_name
            data['emp_nick_name'] = instance.emp_user.nick_name
            data['emp_mobile_number'] = instance.emp_user.mobile_number
            data['emp_address1'] = instance.emp_user.address1
            data['emp_address2'] = instance.emp_user.address2
            data['emp_email'] = instance.emp_user.email
            # Do not include the password in the representation
        else:
            data['emp_first_name'] = None
            data['emp_last_name'] = None
            data['emp_nick_name'] = None
            data['emp_mobile_number'] = None
            data['emp_address1'] = None
            data['emp_address2'] = None
            data['emp_email'] = None

        
        return data
    
    def validate(self, attrs):
        instance = self.instance  # Get the current instance being updated
      
        if instance is not None and attrs.get('emp_email') is not None and str(instance.emp_user.email).strip() == str(attrs.get('emp_email')).strip():
            return super().validate(attrs)
        else:
            User = get_user_model()
            if User.objects.filter(email= attrs.get('emp_email')).exists():
                raise serializers.ValidationError({"emp_email": ["User with this email already exists."]})
                
        return super().validate(attrs)
    @transaction.atomic()
    def create(self, validated_data):

        user=self.context.get('request').user
        print("role is ",user.role)
        if user.role =="Company":
            first_name=validated_data.pop('emp_first_name',"")
            last_name=validated_data.pop('emp_last_name',"")
            nick_name=validated_data.pop('emp_nick_name',"")
            emp_mobile_number=validated_data.pop('emp_mobile_number',None)
            emp_address1=validated_data.pop('emp_address1',None)
            emp_address2=validated_data.pop('emp_address2',None)
            emp_email=validated_data.pop('emp_email',None)
            emp_password=validated_data.pop('emp_password',None)
            validated_data['emp_name']=f"{first_name} {last_name}"
            User = get_user_model()
            if User.objects.filter(email=emp_email).exists():
                raise serializers.ValidationError({"error": "User with this email already exists"})
            
            create_user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                nick_name=nick_name,
                mobile_number=emp_mobile_number,
                address1=emp_address1,
                address2=emp_address2,
                email=emp_email,
                role="Employee"
            )
            create_user.set_password(emp_password)
            validated_data['emp_user']=create_user
            try:
                company_obj=Company.objects.get(custom_user_id=user.id)
                validated_data['company'] = company_obj
            except Company.DoesNotExist:
                serializers.ValidationError({"error":"Company does not exist"})
        
        return super().create(validated_data)

    @transaction.atomic()
    def update(self, instance: Employee, validated_data):
        user = self.context.get('request').user
        if user.role == "Company":
            user_data = {
                'first_name': validated_data.pop('emp_first_name', instance.emp_user.first_name),
                'last_name': validated_data.pop('emp_last_name', instance.emp_user.last_name),
                'nick_name': validated_data.pop('emp_nick_name', instance.emp_user.nick_name),
                'mobile_number': validated_data.pop('emp_mobile_number', instance.emp_user.mobile_number),
                'address1': validated_data.pop('emp_address1', instance.emp_user.address1),
                'address2': validated_data.pop('emp_address2', instance.emp_user.address2),
                'email': validated_data.pop('emp_email', instance.emp_user.email),
            }
            emp_password = validated_data.pop('emp_password', None)
            if emp_password:
                instance.emp_user.set_password(emp_password)
            for attr, value in user_data.items():
                setattr(instance.emp_user, attr, value)
            instance.emp_user.save()

            instance.emp_name = f"{user_data['first_name']} {user_data['last_name']}"
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance

class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAttendance
        fields = ['employee', 'status','date_of_attendance']



class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = ['id', 'name', 'state', 'country']


class CityNightSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(required=False)
    class Meta:
        model = CityNight
        fields = ['id', 'city', 'nights']
    
    def to_representation(self, instance):
        data=super().to_representation(instance)
        data['city_name']=instance.city.name
        return data
   

class TravelDetailsSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(required=False)
  
    class Meta:
        model = Travel_Details
        fields = '__all__'
class ItineraryPackageSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(required=False)
    class Meta:
        model= Itinerary
        fields='__all__'
        extra_kwargs={
            'package':{
                "required": False,
            },
            'activities':{
                "required":False
            }
        }    

class HotelDetailSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(required=False)

    class Meta:
        fields='__all__'
        model=HotelDetails
        extra_kwargs={
            "package":{
                "required": False,
            },
            "hotel":{
                "required": True,
            },

        }  

class CustomisedPackageUpdateSerializer(serializers.ModelSerializer):
    hotel_details=HotelDetailSerializer(many=True,write_only=True)
    travel_details=TravelDetailsSerializer(many=True,write_only=True)
    itineraty=ItineraryPackageSerializer(many=True,write_only=True)
    interests = serializers.MultipleChoiceField(choices=CustomisedPackage.INTEREST_CHOICES)
   
    class Meta:
       fields= '__all__'
       model=CustomisedPackage
       extra_kwargs={
           "package_name":{
               "required":False
           }
       }
    
    def update(self, instance, validated_data):

        city_nights_data = instance.city_nights.all()
        hotel_detail=validated_data.pop('hotel_details', [])
        travel_details=validated_data.pop('travel_details', [])

        for travel in travel_details:
            if travel.get('id'):
                travel_instance=Travel_Details.objects.filter(
                    id=travel.get('id')
                )
                travel_instance.update(**travel)
        itineraty=validated_data.pop('itineraty', [])
        for city_night in city_nights_data:

            for hotel_detls in hotel_detail:
                # print(hotel_detls)
                if hotel_detls.get('id'):
                    #update hotel_detail
                    hote_dtl=HotelDetails.objects.filter(package_id=instance.id,id=hotel_detls.get('id'),citynight_id=city_night.id)
                    print("hotel==>",hote_dtl)
                    if hote_dtl.exists():
                        room_types=RoomType.objects.filter(
                                Q(hotel=hotel_detls.get('hotel'))|
                                Q(rnm__icontains=hotel_detls.get('room_type'))
                                  ).first()
                        per_night_price = room_types.price if room_types else 0
                        total_price = per_night_price * city_night.nights
                        hotel_detls['total_price'] =total_price
                        hote_dtl.update(**hotel_detls)

                # else:
                #     #create new hotel
                #     room_types=RoomType.objects.filter(
                #             Q(hotel=hotel_detls.get('hotel'))|
                #             Q(rnm__icontains=hotel_detls.get('room_type'))
                #               ).first()
                #     per_night_price = room_types.price if room_types else 0
                #     total_price = per_night_price * city_night.nights
                #     hotel_detls['total_price'] =total_price
                #     HotelDetails.objects.create(
                #         package=instance,
                #         citynight=city_night,
                #         **hote_dtl
                #     )
                    
                #     print(room_types)
                
            print("hotel update complete")
            for itiner in itineraty:
                if itiner.get('id'):
                    itiner_instance = Itinerary.objects.get(id=itiner.get('id'))
                     # Update non-ManyToMany fields
                    non_m2m_fields = {key: value for key, value in itiner.items() if key != 'activities'}
                    for key, value in non_m2m_fields.items():
                        setattr(itiner_instance, key, value)
                    itiner_instance.save()

                    # Update ManyToMany fields (activities)
                    activities = itiner.get('activities', [])
                    if activities:
                        itiner_instance.activities.set(activities)
                    else:
                        itiner_instance.activities.clear()

        return super().update(instance, validated_data)


class CustomisedPackageSerializer(serializers.ModelSerializer):
    city_nights = CityNightSerializer(many=True,required=False)
    interests = serializers.MultipleChoiceField(choices=CustomisedPackage.INTEREST_CHOICES)
    del_city_nigths=serializers.ListField(write_only=True,required=False)
    
    class Meta:
        model = CustomisedPackage
        fields='__all__'
        extra_kwargs = {
            "customer":{
                "required": True
            },
            "leaving_from":{
                "required": True
            },
            "package_name":{
                "required": False
            },
        }
    @transaction.atomic()  
    def create(self, validated_data):
        city_nights_data = validated_data.pop('city_nights')
        validated_data['package_name']=F"Trip to {city_nights_data[0].get('city').name}"
        req_user=self.context.get('request').user
        if req_user.role == 'Employee':
            company = Employee.objects.filter(emp_user=req_user).first().company
            validated_data['company']=company
        
        elif req_user.role == 'Company':
            # print(req_user.email)
            company = Company.objects.filter(custom_user_id=req_user.id).first()
            # print("company==>",company)
            validated_data['company'] = company
        validated_data['updated_by'] = req_user
        validated_data['created_by'] = req_user
        package = CustomisedPackage.objects.create(**validated_data)
            
        
        hotel_leaving_date=package.leaving_on
        itenerary_date = package.leaving_on
        print("Leaving",hotel_leaving_date)

        rto=RoadTransportOption.objects.filter(seats__gte=package.number_of_adults).first()
        travel_details=None
        # print("Travel details",rto,city_nights_data[0].get('city'),package.leaving_from)
        if rto:
            print("rto==>",rto)
            travel_details=Travel_Details.objects.create(package=package,road_transport=rto,destination=city_nights_data[0].get('city'),pickup_from=package.leaving_from)

        # Create CityNight instances
        for city_night_data in city_nights_data:
            total_price=None
            city_night=CityNight.objects.create(package=package, **city_night_data)
            hotel_obj=Hotel.objects.filter(city=city_night_data.get('city'),star_rating=package.star_rating)
            if hotel_obj.exists():
                hotel=hotel_obj.first()
                room_types=RoomType.objects.filter(Q(hotel=hotel)
                                                   |
                        Q(rnm__icontains=package.room_type)).first()
                
                per_night_price = room_types.price if room_types else 0
        
            
                total_price = per_night_price * city_night.nights
                hotel_detail={
                    "package":package,
                    "hotel":hotel,
                    "check_in_date":hotel_leaving_date,
                    "check_out_date":hotel_leaving_date + datetime.timedelta(days=city_night.nights),
                    "number_of_rooms":package.number_of_rooms,
                    "room_type":package.room_type,
                    "total_price":total_price,
                    "citynight":city_night,

                }
                print("hotel detail",hotel_detail)
                hotel_details=HotelDetails.objects.create(**hotel_detail)
                hotel_leaving_date=hotel_details.check_out_date
                print(hotel_details)
            
       
            
            # Filter and sort activities based on category and city
           
            category_q = Q()
            for interest in package.interests:
                category_q |= Q(category__icontains=interest)
    
           
            activity_list = list(
                Activity.objects.filter(
                    activity_city=city_night.city
                ).exclude(
                    activity_name__icontains='Departure from'
                ).exclude(
                    activity_name__icontains='Arrival at'
                ).order_by('sequence')
            )


            print("Activtion list",activity_list)
            # Create an iterator to cycle through activities
            activity_cycle = cycle(activity_list)
          
            # Create itinerary entries for each day of the city night stay
            for i in range(city_night.nights):
                # Get the next unique activity from the cycle
                if i==0:
                    activity,is_created = Activity.objects.get_or_create(activity_name__icontains=f"Arrival at {city_night.city.name}",activity_city=city_night.city)
                    print("Activity=======>",activity,is_created)
                else:
                    else_activity,is_created =Activity.objects.get_or_create(activity_name="Day at Leisure",activity_city=city_night.city,sequence=2,category=['leisure'],activity_desc=f"Explore {city_night.city.name} on your own")
                    activity = next(activity_cycle, else_activity)
                itinerary_date = itenerary_date + datetime.timedelta(days=i)
                itinerary = Itinerary.objects.create(
                    package=package, 
                    days=itinerary_date, 
                    citynight=city_night
                   
                )   
               
                print("Created itinerary",city_night.city.name,itinerary,itinerary.days)
                if activity:
                   
                    print(activity.activity_city.name)
                    # Create itinerary entry with the activity
                    itinerary.activities.add(activity)
                else:
                    # Handle the case where there are fewer activities than days
                    print(f"Warning: Insufficient activities for {city_night.city}")
    
            # Update the itenerary_date for the next city
            itenerary_date = itinerary_date + datetime.timedelta(days=1)

        # add last day of package
        last_iti=Itinerary.objects.filter(package_id=package.id).last()
        itinerary = Itinerary.objects.create(
                    package=package, 
                    days=last_iti.days+datetime.timedelta(days=1), 
                   citynight=last_iti.citynight,
                  
                ) 
        activity, is_created=Activity.objects.get_or_create(activity_name=f"Departure from {itinerary.citynight.city.name}",activity_city=city_night.city)
        itinerary.activities.add(activity)  
        return package
    
    def delete_city_nights(self,del_list,package:CustomisedPackage):
    
        for cn_id in del_list:
            cn=CityNight.objects.filter(id=cn_id)
            if cn.exists():
                Travel_Details.objects.filter(package=package,destination=cn.first().city).delete()

        CityNight.objects.filter(id__in=del_list).delete()
        self.reschedule(package)
    def delete_hotels_detail(self,package,citynight):
        hotel_detail =HotelDetails.objects.filter(package=package,citynight=citynight)
        hotel_detail.delete()
    def delete_itinerary(self,package,citynight):
        itinerary_detail =Itinerary.objects.filter(package=package,citynight=citynight)
        itinerary_detail.delete()


    def add_hotel_detail(self,package:CustomisedPackage,city_night:CityNight,hotel_leaving_date):
        hotel_obj=Hotel.objects.filter(city=city_night.city,star_rating=package.star_rating)
        if hotel_obj.exists():
                hotel=hotel_obj.first()
                room_types=RoomType.objects.filter(Q(hotel=hotel)
                                                   |
                        Q(rnm__icontains=package.room_type)).first()
                
                per_night_price = room_types.price if room_types else 0
        
            
                total_price = per_night_price * city_night.nights
                hotel_detail={
                    "package":package,
                    "hotel":hotel,
                    "check_in_date":hotel_leaving_date,
                    "check_out_date":hotel_leaving_date + datetime.timedelta(days=city_night.nights),
                    "number_of_rooms":package.number_of_rooms,
                    "room_type":package.room_type,
                    "total_price":total_price,
                    "citynight":city_night,

                }
                print("hotel detail",hotel_detail)
                hotel_details=HotelDetails.objects.create(**hotel_detail)
                hotel_leaving_date=hotel_details.check_out_date
                print(hotel_details)
                
    
    def add_itinerary(self,package:CustomisedPackage,city_night:CityNight,itin_city_change_last_date):
            category_q = Q()
            for interest in package.interests:
                category_q |= Q(category__icontains=interest)
    
           
            activity_list = list(
                Activity.objects.filter(
                    activity_city=city_night.city
                ).exclude(
                    activity_name__icontains='Departure from'
                ).exclude(
                    activity_name__icontains='Arrival at'
                ).order_by('sequence')
            )


            print("Activtion list",activity_list)
            # Create an iterator to cycle through activities
            activity_cycle = cycle(activity_list)
          
            # Create itinerary entries for each day of the city night stay
            for i in range(city_night.nights):
                # Get the next unique activity from the cycle
                if i==0:
                    activity,is_created = Activity.objects.get_or_create(activity_name__icontains=f"Arrival at {city_night.city.name}",activity_city=city_night.city)
                    print("Activity=======>",activity,is_created)
                else:
                    else_activity,is_created =Activity.objects.get_or_create(activity_name="Day at Leisure",activity_city=city_night.city,sequence=2,category=['leisure'],activity_desc=f"Explore {city_night.city.name} on your own")
                    activity = next(activity_cycle, else_activity)
                itinerary_date = itin_city_change_last_date + datetime.timedelta(days=i)
                itinerary = Itinerary.objects.create(
                    package=package, 
                    days=itinerary_date, 
                    citynight=city_night
                   
                )   
               
                print("Created itinerary",city_night.city.name,itinerary,itinerary.days)
                if activity:
                   
                    print(activity.activity_city.name)
                    # Create itinerary entry with the activity
                    itinerary.activities.add(activity)
                else:
                    # Handle the case where there are fewer activities than days
                    print(f"Warning: Insufficient activities for {city_night.city}")
    
            # Update the itenerary_date for the next city
            itin_city_change_last_date = itinerary_date + datetime.timedelta(days=1)
    @transaction.atomic()
    def update(self, instance, validated_data):
        city_nights_data = validated_data.pop('city_nights',[])
        del_city_nigths = validated_data.pop('del_city_nigths',[])
        if len(del_city_nigths)>0:
            self.delete_city_nights(del_city_nigths,instance)
        
        hotel_leaving_date=validated_data.get('leaving_on', instance.leaving_on)
        itin_city_change_last_date =validated_data.get('leaving_on', instance.leaving_on)
        is_change_city=False
        instance.leaving_on=validated_data.get('leaving_on', instance.leaving_on)
        for city_night in city_nights_data:
            city = city_night.get('city')
            city_night_id = city_night.get('id', None)
            if city_night_id:
                city_night_obj = CityNight.objects.get(id=city_night_id, package=instance)
                if city_night_obj.city.name !=city.name or city_night_obj.nights != city_night.get('nights',city_night_obj.nights) or city_night_obj.city.name !=city.name:
                    city_night_obj.nights=city_night.get('nights',city_night_obj.nights)
                    city_night_obj.city=city
                    self.delete_hotels_detail(instance,city_night_obj)
                    self.delete_itinerary(instance,city_night_obj)
                    self.add_hotel_detail(instance,city_night_obj,hotel_leaving_date)
                    self.add_itinerary(instance,city_night_obj,itin_city_change_last_date)
                    is_change_city=True
                    city_night_obj.save()
        
        
            else:
                
                it=Itinerary.objects.filter(package=instance).order_by('date')
                if it.exists():
                    hotel_leaving_date=it.last().days
                
                city_night_obj=CityNight.objects.create(package=instance, **city_night)
                self.add_hotel_detail(instance,city_night_obj,hotel_leaving_date)
                self.add_itinerary(instance,city_night_obj,itin_city_change_last_date)
                is_change_city=True
                              


        if is_change_city:
            last_iti=Itinerary.objects.filter(package_id=instance.id).last()
            itinerary = Itinerary.objects.create(
                        package=instance, 
                        days=last_iti.days+datetime.timedelta(days=1), 
                       citynight=last_iti.citynight,
                    ) 
            activity, is_created=Activity.objects.get_or_create(activity_name=f"Departure from {itinerary.citynight.city.name}",activity_city=city_night_obj.city)
            itinerary.activities.add(activity)  
        self.reschedule(instance)       
        CustomisedPackage.objects.filter(id=instance.id).update(**validated_data)
        return validated_data
    
    def reschedule(self,package):
        itiners=Itinerary.objects.filter(package=package).order_by('days')
        start_itin_date=package.leaving_on
        for it in itiners:
            print(start_itin_date)
            it.days=start_itin_date
            it.save()
            start_itin_date=start_itin_date + datetime.timedelta(days=1)
    # @transaction.atomic()
    # def update(self, instance, validated_data):
    #     city_nights_data = validated_data.pop('city_nights',[])
    #     del_city_nigths = validated_data.pop('del_city_nigths',[])
    #     CityNight.objects.filter(id__in=del_city_nigths).delete()
    #     # print(city_nights_data)
    #     if validated_data.get('interests'):
    #         validated_data['interests']=list(validated_data.get('interests'))
    #     itenerary_date = instance.leaving_on
    #     print("trip started at: " , itenerary_date)
    #     current_night = 1
    #     for city_night in city_nights_data:
    #         city = city_night.get('city')
    #         city_night_id = city_night.get('id', None)
         
    #         if city_night_id:
    #             city_night_obj = CityNight.objects.get(id=city_night_id, package=instance)
                
    #             if city_night_obj.city.name !=city.name and city_night_obj.nights != city_night.get('nights',city_night.nights) or city_night_obj.city.name !=city.name:
    #                 print("change city_name and night")
                    
    #             elif city_night_obj.nights != city_night.get('nights',city_night_obj.nights):
    #                     print("change night")
                    
                   

    #                 # if city_night_obj.nights < city_night.get('nights',city_night_obj.nights):
    #                     # add night
    #                     add_night=city_night.get('nights') - city_night_obj.nights
    #                     print("add night",add_night)
                       
    #                     for i in range(city_night['nights']):
    #                         # select first 
    #                         if i==0:
    #                             activity,is_created = Activity.objects.get_or_create(activity_name__icontains=f"Arrival at {city_night_obj.city.name}",activity_city=city_night_obj.city)
    #                         elif i==city_night['nights']:
    #                             activity, is_created=Activity.objects.get_or_create(activity_name=f"Departure from {city_night_obj.city.name}",activity_city=city_night_obj.city)

    #                         else:
    #                             activity,is_created =Activity.objects.get_or_create(activity_name="Day at Leisure",activity_city=city_night_obj.city,category=['leisure'],activity_desc=f"Explore {city_night_obj.city.name} on your own")
                            
    #                         itinerary_date = itenerary_date + datetime.timedelta(days=i)
                            
    #                         itierary=Itinerary.objects.filter(package=instance,citynight_id=city_night_id,days=itinerary_date.strftime('%Y-%m-%d'))
    #                         print(itinerary_date.strftime('%Y-%m-%d'))
    #                         current_night += 1
    #                         if itierary.exists():
    #                             if i!=city_night['nights']+1:
    #                                 act = Activity.objects.filter(activity_name__icontains="Departure from", activity_city=city)
    #                                 if act.exists():
    #                                     if itierary.first().activities.filter(id__in=act.values_list('id', flat=True)).exists():
    #                                         # Activity exists in the itinerary's activities
    #                                         itierary.first().activities.clear
    #                                         itierary.first().activities.add(activity)
                                            
    #                             itierary.update(
    #                                 days=itinerary_date
    #                             )
    #                         else:
    #                             print("not found")
    #                             itinerary = Itinerary.objects.create(
    #                                     package=instance, 
    #                                     days=itinerary_date, 
    #                                     citynight_id=city_night_id

    #                                 )   
               
    #                             # print("Created itinerary",city_night_obj.city.name,itinerary,itinerary.days)
    #                             if activity:
                                
    #                                 print("",activity.activity_city.name,activity.activity_name)
    #                                 # Create itinerary entry with the activity
    #                                 itinerary.activities.add(activity)
    #                             else:
    #                                 # Handle the case where there are fewer activities than days
    #                                 print(f"Warning: Insufficient activities for {city_night.city}")
                        
    #                         # print(current_night,itenerary_date.strftime('%Y-%m-%d'),itierary)
    #                         # itenerary_date=itenerary_date + datetime.timedelta(days=1)

    #                     # Itiners=Itinerary.objects.filter(citynight=city_night,package=instance).order_by('days')
                        
    #                     # for itiner in Itiners:
    #                     #     print(itiner.days)

    #                     # print("last==>",Itiners)
    #                 # elif city_night_obj.nights > city_night.get('nights',city_night_obj.nights):
    #                 #     pass

    #                     # less night

    #          # Update the itenerary_date for the next city
    #         itenerary_date = itinerary_date + datetime.timedelta(days=1)

                     

        #     for _ in range(city_night['nights']):
        #         expanded_city_nights.append({
        #             'id': city_night['id'],
        #             'city': city_night['city'],
        #             'night': current_night,
        #             "city_night": city_night,
        #             'date':itenerary_date + datetime.timedelta(days=current_night - 1)
        #         })
                
        #         current_night += 1
        # for cn in expanded_city_nights:
        #     city_night_id = cn.get('id', None)
        #     if city_night_id:
        #         itierary=Itinerary.objects.filter(package=instance,citynight_id=cn.get('id'),days=date_obj)
        #         city_night = CityNight.objects.get(id=city_night_id, package=instance)
        
       
        # expanded_city_nights = []
        # current_night = 1
        # for city_night in city_nights_data:
        #     for _ in range(city_night['nights']):
        #         expanded_city_nights.append({
        #             'id': city_night['id'],
        #             'city': city_night['city'],
        #             'night': current_night,
        #             "city_night": city_night,
        #             'date':itenerary_date + datetime.timedelta(days=current_night - 1)
        #         })
                
        #         current_night += 1
        # for cn in expanded_city_nights:
        #     date_str = cn.get('date')
        #     date_obj = date_str.strftime('%Y-%m-%d')
        #     city_night_id = cn.get('id', None)
        #     if city_night_id:
        #         itierary=Itinerary.objects.filter(package=instance,citynight_id=cn.get('id'),days=date_obj)
        #         city_night = CityNight.objects.get(id=city_night_id, package=instance)
                
       
        # for city_night_data in city_nights_data:
        #     city = city_night_data.pop('city')
        #     city_night_id = city_night_data.get('id', None)
        #     city_night_data['city'] = city
            
        #     if city_night_id:
        #         city_night = CityNight.objects.get(id=city_night_id, package=instance)
                
        #         if city_night.city.name !=city.name and city_night.nights != city_night_data.get('nights',city_night.nights) or city_night.city.name !=city.name:
        #             print("change city_name and night")
                    
        #         elif city_night.nights != city_night_data.get('nights',city_night.nights):
        #             print("change night")
                    
        #             if city_night.nights < city_night_data.get('nights',city_night.nights):
        #                 # add night
        #                 add_night=city_night_data.get('nights') - city_night.nights
        #                 print("add night",add_night)

        #                 Itiners=Itinerary.objects.filter(citynight=city_night,package=instance).order_by('days')
                        
        #                 for itiner in Itiners:
        #                     print(itiner.days)

        #                 print("last==>",Itiners)
        #             elif city_night.nights > city_night_data.get('nights',city_night.nights):
        #                 # less night
        #                 pass

        #         else:
        #             print("else")
            #     # city_night.city = city
            #     # city_night.nights = city_night_data.get('nights', city_night.nights)
            #     # city_night.save()

            # else:
            #     CityNight.objects.create(package=instance, city=city, **city_night_data)
        # CustomisedPackage.objects.filter(id=instance.id).update(**validated_data)
        # return validated_data
    def add_nights(self, city_night, additional_nights):
        itineraries = Itinerary.objects.filter(citynight=city_night, package=city_night.package).order_by('days')
        last_itinerary = itineraries.last()
        last_day = last_itinerary.days if last_itinerary else city_night.package.leaving_on
        
        for i in range(additional_nights):
            new_day = last_day + datetime.timedelta(days=i+1)
            act,is_created=Activity.objects.get_or_create(activity_name="Day at Leisure",activity_city__name=city_night.city.name,sequence=2,category=['leisure'],activity_desc=f"Explore {city_night.city.name} on your own")
            itiner=Itinerary.objects.create(
                package=city_night.package,
                citynight=city_night,
                days=new_day,
                
                status='PENDING'
            )
            itiner.activities.add(act)

        last=Itinerary.objects.filter(
                package=city_night.package,
                citynight_id=city_night.id).order_by('days').last()
        activity, is_created=Activity.objects.get_or_create(activity_name=f"Departure from {last.citynight.city.name}",activity_city=city_night.city)
        last.activities.set(activity)
        print("add night last Itinerary",last)

    def reduce_nights(self, city_night, reduced_nights):
        itineraries = Itinerary.objects.filter(citynight=city_night, package=city_night.package).order_by('days')
        itineraries_to_delete = itineraries.reverse()[:reduced_nights]
        Itinerary.objects.filter(id__in=[itinerary.id for itinerary in itineraries_to_delete]).delete()


class RoadTransportSerializer(serializers.ModelSerializer):
    destination_id = serializers.CharField(read_only=True, source="destination.id")
    destination = serializers.CharField(read_only=True, source="destination.name")
    pickup_from_id = serializers.CharField(read_only=True, source="pickup_from.id")
    pickup_from = serializers.CharField(read_only=True, source="pickup_from.name")
    class Meta:
        model = RoadTransportOption
        fields = '__all__'
  


class ActivitySerializer(serializers.ModelSerializer):
    category = serializers.MultipleChoiceField(choices=Activity.category_choices)
  
    class Meta:
        model=Activity
        fields= '__all__'
    
    def to_representation(self, instance:Activity):
        data=super().to_representation(instance)
        data['activity_city']={
            "city_id": instance.activity_city.id,
            "city": instance.activity_city.name,
            "country_id": instance.activity_city.country.id,
            "country": instance.activity_city.country.name,
            "state_id": instance.activity_city.state.id,
            "state": instance.activity_city.state.name,
        }
        return data




class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model= Country
        fields='__all__'
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model= States
        fields='__all__'
class CitieSerializer(serializers.ModelSerializer):
    class Meta:
        model= Cities
        fields='__all__'
    
    def to_representation(self, instance:Cities):
        data=super().to_representation(instance)
        data['country_name']=instance.country.name
        if instance.state:
            data['state_name']=instance.state.name
    
        return data
    

class HotelRoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= RoomType
        fields='__all__'


class HotelSerializer(serializers.ModelSerializer):
    rooms_type=HotelRoomTypeSerializer(many=True)
    class Meta:
        model= Hotel
        fields='__all__'


class ItineraryPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model= Itinerary
        fields='__all__'
        extra_kwargs={
            
        }    

    def to_representation(self, instance):

        data=super().to_representation(instance)
        
        return data

class ItinerarySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Itinerary
        fields = '__all__'
        extra_kwargs={
            "activities":{"required": False},
            "days": {"required": False}
        }
    def to_representation(self, instance:Itinerary):
        data=super().to_representation(instance)
        data['activities']=instance.activities.all().values()
        data['city_id']=instance.citynight.city.id
        data['city_name']=instance.citynight.city.name
        return  data
    

