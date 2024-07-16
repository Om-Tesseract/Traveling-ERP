from django.db import models
from authentication.models import CustomUser
# Create your models here.
from multiselectfield import MultiSelectField
from utils.common_model import BaseModel



class Country(models.Model):
    name=models.CharField(max_length=50,unique=True)
    iso3=models.CharField(max_length=30,null=True)
    iso2=models.CharField(max_length=30,null=True)
    numeric_code=models.CharField(max_length=20,null=True)
    phone_code=models.CharField(max_length=20,null=True)  
    currency=models.CharField(max_length=50,null=True)
    currency_name=models.CharField(max_length=50,null=True)
    currency_symbol=models.CharField(max_length=50,null=True)
    region=models.CharField(max_length=50,null=True)
    nationality=models.CharField(max_length=50,null=True)
    emojiU=models.CharField(max_length=50,null=True)
    def __str__(self) -> str:
        return self.name
class States(models.Model):
    name= models.CharField(max_length=60)
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name="country_states_set")
    state_code=models.CharField(max_length=20,null=True)

class Cities(models.Model):
    name=models.CharField(max_length=60,)
    state= models.ForeignKey(States,on_delete=models.CASCADE,related_name="state_city_set")
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name="country_city_set")

    def __str__(self) -> str:
        return f"{self.name} {self.state.name}"


class RoadTransportOption(models.Model):
    vehicle_type = models.CharField(max_length=100)
    seats = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   

    def __str__(self):
       
        return f"{self.vehicle_type} (Seats: {self.seats} people)"


class Company(models.Model):
    custom_user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name="company_set")
    website = models.CharField(max_length=50, null=True, blank=True)
    heading_logo = models.ImageField(upload_to="heading_logos",null=True, blank=True)
    company_logo = models.ImageField(upload_to="company_logos",null=True, blank=True)
    primary_color = models.CharField(max_length=100, null=True, blank=True)
    secondary_color = models.CharField(max_length= 100, null=True, blank=True)
    primary_txt_color=models.CharField(max_length=60,null=True)
    secondary_txt_color=models.CharField(max_length=60,null=True)
    # class Meta:
    #     db_table = 'company'
    def __str__(self) -> str:
        return f"{self.custom_user.first_name}"
class Employee(BaseModel):
    emp_name = models.CharField(max_length=100)
    emp_salary = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    emp_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="employee_user",null=True,blank=True)
    emp_department = models.CharField(max_length=100,null=True,blank=True)
    emp_dob= models.DateField(null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employee_company",null=True,blank=True)
    
    class Meta:
        ordering=["emp_name"]

    def __str__(self):
        return self.emp_name
    
class EmployeeAttendance(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True,blank=True)
    date_of_attendance=models.DateTimeField(null=True,blank=True)
    statuses = (
        ("Present", "Present"),
        ("Absent","Absent"),
    )
    status = models.CharField(max_length=50, choices=statuses, default="select status")

class Customer(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE,related_name="customer_company",null=True,blank=True)
    name = models.CharField(max_length=100,)
    address = models.CharField(max_length=255,null=True,blank=True)
    mobile_number = models.CharField(max_length=15,)
    country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.CASCADE)
    state = models.ForeignKey(States,on_delete=models.CASCADE,null=True,blank=True)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE,null=True,blank=True)
    # country = models.CharField(max_length=50,null=True,blank=True)
    # state = models.CharField(max_length=50,null=True,blank=True)
    # city = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(null=True, blank=True)
    def __str__(self):
        return self.name
    

class Package(models.Model):
    package_name = models.CharField(max_length=100,null=True,blank=True)
    package_location = models.CharField(max_length=100,null=True,blank=True)
    number_of_persons = models.JSONField(null=True,blank=True)
    package_link = models.URLField(null=True,blank=True)
    custom_user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="customuser_package",null=True,blank=True)
    def __str__(self):
        return self.package_name
    


class Nationality(models.Model):
    nationality_choice=models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return f'{self.nationality_choice}'


class CustomisedPackage(BaseModel):
    package_name=models.CharField(max_length=200,)
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,related_name="customer_package",null=True,blank=True)
    leaving_from= models.ForeignKey(Cities, on_delete=models.SET_NULL,related_name="leaving_city",null=True,blank=True)
    nationality=models.ForeignKey(Country,on_delete=models.SET_NULL,related_name="package_nationality",null=True,blank=True)
    leaving_on=models.DateTimeField()
    number_of_rooms = models.IntegerField(default=1)
    number_of_adults = models.IntegerField(default=0)
    number_of_children = models.IntegerField(default=0)
    company=models.ForeignKey(Company,null=True,on_delete=models.CASCADE)


    INTEREST_CHOICES = [
        ('Honeymoon', 'Honeymoon'), 
        ('Luxury', 'Luxury'),
        ('Leisure', 'Leisure'),
        ('Spa', 'Spa'),
        ('History', 'History'),
        ('Art and Culture', 'Art and Culture'),
        ('Adventure', 'Adventure'),
        ('Shopping', 'Shopping'),
        ('Entertainment', 'Entertainment'),
        ('Nightlife', 'Nightlife'),
    ]
    interests = MultiSelectField(max_length=200, choices=INTEREST_CHOICES,null=True)

    TRAVEL_CHOICES=[
        ('couple','Couple'),
        ('family','Family'),
        ('friends','Friends'),
    ]
    who_is_travelling=models.CharField(max_length=50,choices=TRAVEL_CHOICES,null=True)

    #checkbox fields
    #couple
    pregnant_women=models.BooleanField(default=False)
    elderly_people=models.BooleanField(default=False)
    with_walking_difficulty=models.BooleanField(default=False)
    #family
    teenager=models.BooleanField(default=False)
    #friends
    women_only=models.BooleanField(default=False)
    men_only=models.BooleanField(default=False)
  
    room_type=models.CharField(max_length=20,null=True)
    star_rating=models.IntegerField(default=3)
    add_transfers=models.BooleanField(default=False)
    add_tours_and_travels=models.BooleanField(default=False)
    itinerary_created=models.BooleanField(default=False)

class CityNight(models.Model):
    city = models.ForeignKey(Cities, on_delete=models.CASCADE)
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, related_name='city_nights')
    nights = models.IntegerField()




class Travel_Details(models.Model):
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, null=True, blank=True)
    vehicles = models.JSONField(null=True, blank=True)
    is_flights=models.BooleanField(default=False)
    road_transport=models.ForeignKey(RoadTransportOption,on_delete=models.CASCADE,null=True,blank=True)
    PNR = models.CharField(max_length=100, null=True, blank=True)
    destination = models.ForeignKey(Cities,null=True,blank=True,on_delete=models.CASCADE,related_name="destination")
    pickup_from = models.ForeignKey(Cities,null=True, blank=True,on_delete=models.CASCADE,related_name="pickup_from")

# class Expansion    


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True)
    area=models.CharField(max_length=50,null=True,blank=True)
    city = models.ForeignKey('Cities', on_delete=models.CASCADE, related_name='hotels')
    star_rating = models.IntegerField(null=True, blank=True)
    rate=models.CharField(max_length=20,null=True)
    desc=models.TextField(null=True,blank=True)
    contact_info = models.JSONField(null=True, blank=True)  # Contact details like phone, email, etc.
    image_url = models.URLField(max_length=200,null=True,blank=True)
    ln=models.FloatField(null=True, blank=True)
    lt=models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.name
    
class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE,related_name="rooms_type")
    rnm = models.CharField("room name",max_length=255)
    meal_plan = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    amenity = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.rnm} - {self.hotel.name}"


class HotelDetails(models.Model):
    
    package = models.ForeignKey('CustomisedPackage', on_delete=models.CASCADE, related_name='hotel_details')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    citynight= models.ForeignKey(CityNight, on_delete=models.CASCADE,null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    room_type = models.CharField(max_length=100)  # e.g., Single, Double, Suite
    number_of_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_requests = models.TextField(null=True, blank=True)  # Any special requests made by the customer

    def __str__(self):
        return f'{self.hotel.name} - {self.room_type}'


class Activity(models.Model):
    category_choices = [
        ('honeymoon', 'Honeymoon'),
        ('luxury', 'Luxury'),
        ('leisure', 'Leisure'),
        ('spa', 'Spa'),
        ('history', 'History'),
        ('art_and_culture', 'Art and Culture'),
        ('adventure', 'Adventure'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment'),
        ('nightlife', 'Nightlife'),
    ]
    
    
    category = MultiSelectField(max_length=250, choices=category_choices)
    duration = models.CharField(max_length=30, null=True, blank=True)  
    age_limit = models.IntegerField(null=True, blank=True)
    activity_name = models.CharField(max_length=350)
    sequence=models.IntegerField(null=True, blank=True)
    activity_desc = models.TextField(null=True, blank=True)
    activity_city = models.ForeignKey(Cities, on_delete=models.CASCADE, related_name="activities_in_city",null=True)

    def __str__(self):
        return self.activity_name if self.activity_name else "Activity"




class Itinerary(models.Model):
    statues_choices=[
      ("PENDING","PENDING"),
      ("COMPLETED","COMPLETED"),
    ]
    package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE,)
    citynight= models.ForeignKey(CityNight, on_delete=models.CASCADE,null=True)
    days=models.DateField()
    activities=models.ManyToManyField(Activity,related_name="Itinrtary_activities",)
    activity_input=models.TextField(null=True,blank=True)
    status=models.CharField(max_length=60,default="PENDING",choices=statues_choices)
  
    class Meta:
        get_latest_by = "days"