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

class States(models.Model):
    name= models.CharField(max_length=60)
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name="country_states_set")
    state_code=models.CharField(max_length=20,null=True)

class Cities(models.Model):
    name=models.CharField(max_length=60,)
    state= models.ForeignKey(States,on_delete=models.CASCADE,related_name="state_city_set")
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name="country_city_set")

    
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
    

class City(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f'{self.name}, {self.state}, {self.country}'

class Nationality(models.Model):
    nationality_choice=models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return f'{self.nationality_choice}'


class CustomisedPackage(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,related_name="customer_package",null=True,blank=True)
    leaving_from= models.ForeignKey(City, on_delete=models.CASCADE,related_name="leaving_city",null=True,blank=True)
    nationality=models.ForeignKey(Nationality,on_delete=models.SET_NULL,related_name="nationality",null=True,blank=True)
    leaving_on=models.DateTimeField(auto_now=True)
    number_of_rooms = models.IntegerField(null=True,blank=True)
    number_of_adults = models.IntegerField(null=True,blank=True)
    number_of_children = models.IntegerField(null=True,blank=True)

    INTEREST_CHOICES = [
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
    interests = MultiSelectField(max_length=200, choices=INTEREST_CHOICES)

    TRAVEL_CHOICES=[
        ('couple','Couple'),
        ('family','Family'),
        ('friends','Friends'),
    ]
    who_is_travelling=models.CharField(max_length=50,choices=TRAVEL_CHOICES)

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

    STAR_CHOICES=[
        ('3_star','3 Stars'),
        ('4_star','4 Stars'),
        ('5_star','5 Stars'),
    ]
    star_rating=models.CharField(max_length=20,choices=STAR_CHOICES,default="Recommended")
    add_transfers=models.BooleanField(default=False)
    add_tours_and_travels=models.BooleanField(default=False)

    itinerary_created=models.BooleanField(default=False)

class CityNight(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, related_name='city_nights')
    nights = models.IntegerField()
    

class Travel_Details(models.Model):
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, null=True, blank=True)
    destinations = models.JSONField(null=True, blank=True)  
    vehicles = models.JSONField(null=True, blank=True)
    PNR = models.CharField(max_length=100, null=True, blank=True)
    hotel_details=models.JSONField(null=True,blank=True)


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
    
    category = models.CharField(max_length=50, choices=category_choices, null=True, blank=True)
    duration = models.CharField(max_length=300, null=True, blank=True)  # in hours
    age_limit = models.IntegerField(null=True, blank=True)
    activity_name = models.CharField(max_length=40, null=True, blank=True)
    activity_desc = models.CharField(max_length=300, null=True, blank=True)
    activity_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="activities_in_city",null=True,blank=True)

    def __str__(self):
        return self.activity_name if self.activity_name else "Activity"

class Itinerary(models.Model):
    package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE,null=True,blank=True)
    days=models.DateField()
    activities=models.ManyToManyField(Activity)
    activity_input=models.TextField(null=True,blank=True)
    travel_details=models.ForeignKey(Travel_Details,on_delete=models.SET_NULL,null=True,blank=True)
