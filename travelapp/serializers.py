# serializers.py
from rest_framework import serializers
from api.models import Company,Customer,Package,Employee,EmployeeAttendance,CustomisedPackage, CityNight, Cities, Nationality, Travel_Details,Activity,Itinerary

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAttendance
        fields = ['employee', 'status','date_of_attendance']



class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
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
        