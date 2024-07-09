
# serializers.py
from rest_framework import serializers
from api.models import Company,Customer,Package,Employee,EmployeeAttendance,CustomisedPackage, CityNight, City, Nationality, Travel_Details,Activity,Itinerary,Country,States,Cities
from django.contrib.auth import get_user_model
from django.db import transaction
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
    emp_nick_name=serializers.CharField(write_only=True,allow_null=True,required=False)
    emp_last_name=serializers.CharField(write_only=True)
    emp_mobile_number=serializers.CharField(write_only=True)
    emp_address1=serializers.CharField(write_only=True,allow_null=True,required=False)
    emp_address2=serializers.CharField(write_only=True,allow_null=True,required=False)
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
        model = City
        fields = ['id', 'name', 'state', 'country']

class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = ['id', 'name']

class CityNightSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = CityNight
        fields = ['id', 'city', 'nights']

    def create(self, validated_data):
        city_data = validated_data.pop('city')
        city, created = City.objects.get_or_create(**city_data)
        city_night = CityNight.objects.create(city=city, **validated_data)
        return city_night

class CustomisedPackageSerializer(serializers.ModelSerializer):
    city_nights = CityNightSerializer(many=True)
    interests = serializers.MultipleChoiceField(choices=CustomisedPackage.INTEREST_CHOICES)

    class Meta:
        model = CustomisedPackage
        fields = [
            'id', 'leaving_from', 'nationality', 'leaving_on', 'number_of_rooms', 'number_of_adults',
            'number_of_children', 'interests', 'who_is_travelling', 'pregnant_women', 'elderly_people',
            'with_walking_difficulty', 'teenager', 'women_only', 'men_only', 'star_rating', 'add_transfers',
            'add_tours_and_travels', 'city_nights'
        ]
        
    def create(self, validated_data):
        city_nights_data = validated_data.pop('city_nights')
        package = CustomisedPackage.objects.create(**validated_data)
        for city_night_data in city_nights_data:
            city_data = city_night_data.pop('city')
            city, created = City.objects.get_or_create(**city_data)
            CityNight.objects.create(package=package, city=city, **city_night_data)
        return package

    def update(self, instance, validated_data):
        city_nights_data = validated_data.pop('city_nights')
        instance.leaving_from = validated_data.get('leaving_from', instance.leaving_from)
        instance.nationality = validated_data.get('nationality', instance.nationality)
        instance.leaving_on = validated_data.get('leaving_on', instance.leaving_on)
        instance.number_of_rooms = validated_data.get('number_of_rooms', instance.number_of_rooms)
        instance.number_of_adults = validated_data.get('number_of_adults', instance.number_of_adults)
        instance.number_of_children = validated_data.get('number_of_children', instance.number_of_children)
        instance.interests = validated_data.get('interests', instance.interests)
        instance.who_is_travelling = validated_data.get('who_is_travelling', instance.who_is_travelling)
        instance.pregnant_women = validated_data.get('pregnant_women', instance.pregnant_women)
        instance.elderly_people = validated_data.get('elderly_people', instance.elderly_people)
        instance.with_walking_difficulty = validated_data.get('with_walking_difficulty', instance.with_walking_difficulty)
        instance.teenager = validated_data.get('teenager', instance.teenager)
        instance.women_only = validated_data.get('women_only', instance.women_only)
        instance.men_only = validated_data.get('men_only', instance.men_only)
        instance.star_rating = validated_data.get('star_rating', instance.star_rating)
        instance.add_transfers = validated_data.get('add_transfers', instance.add_transfers)
        instance.add_tours_and_travels = validated_data.get('add_tours_and_travels', instance.add_tours_and_travels)
        instance.save()

        for city_night_data in city_nights_data:
            city_data = city_night_data.pop('city')
            city, created = City.objects.get_or_create(**city_data)
            city_night_id = city_night_data.get('id', None)
            if city_night_id:
                city_night = CityNight.objects.get(id=city_night_id, package=instance)
                city_night.city = city
                city_night.nights = city_night_data.get('nights', city_night.nights)
                city_night.save()
            else:
                CityNight.objects.create(package=instance, city=city, **city_night_data)

        return instance
    

class TravelDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel_Details
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Activity
        fields= '__all__'

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model=Itinerary 
        fields='__all__'
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