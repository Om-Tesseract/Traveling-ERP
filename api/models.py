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
    name=models.CharField(max_length=60, )
    state= models.ForeignKey(States,on_delete=models.CASCADE,related_name="state_city_set")
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name="country_city_set")
    img=models.ImageField(upload_to="city_images", blank=True, null=True)
    img_url=models.URLField(null=True,blank=True)
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
    statues_choices=[
      ("PENDING","PENDING"),
      ("COMPLETED","COMPLETED"),
    ]
    status=models.CharField(max_length=60,default="PENDING",choices=statues_choices)
  
class CityNight(models.Model):
    city = models.ForeignKey(Cities, on_delete=models.CASCADE)
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, related_name='city_nights')
    # sequence = models.IntegerField(default=1)
    nights = models.IntegerField()

class Flight_Details(models.Model):
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, null=True, blank=True)
    destination_to = models.ForeignKey(Cities,on_delete=models.CASCADE,related_name="flight_destination")
    ret_destination_to = models.ForeignKey(Cities,null=True,blank=True,on_delete=models.CASCADE,related_name="ret_destination")
    pickup_from = models.ForeignKey(Cities,on_delete=models.CASCADE,related_name="flight_pickup_from")
    ret_pickup_from = models.ForeignKey(Cities,null=True, blank=True,on_delete=models.CASCADE,related_name="ret_pickup_from")
    airlines=models.CharField(max_length=100,null=True)
    sequence=models.IntegerField()
    depart_on=models.DateField()
    return_on=models.DateField(null=True, blank=True)
    flt_class=models.CharField(max_length=50)
    PNR = models.CharField(max_length=100, null=True, blank=True)
    type=models.CharField(max_length=30,default="Open Jaw")
    
class Travel_Details(models.Model):
    package = models.ForeignKey(CustomisedPackage, on_delete=models.CASCADE, null=True, blank=True)
    road_transport=models.ForeignKey(RoadTransportOption,on_delete=models.CASCADE,null=True,blank=True)
    PNR = models.CharField(max_length=100, null=True, blank=True)
    destination = models.ForeignKey(Cities,null=True,blank=True,on_delete=models.CASCADE,related_name="destination")
    pickup_from = models.ForeignKey(Cities,null=True, blank=True,on_delete=models.CASCADE,related_name="pickup_from")


def default_amenities():
    return {
        "Accessibility": [
            "Lift Elevator"
        ],
        "Available in All Rooms": [
            "Air Conditioning",
            "Kitchenette",
            "Ironing Facilities"
        ],
        "Dining, Drinking and Snacking": [
            "Mini Bar",
            "Restaurant",
            "Room Service"
        ],
        "Things to do, ways to relax": [
            "Lawn",
            "Tours"
        ],
        "Fitness and Recreation": [
            "Indoor Games"
        ],
        "Getting Around": [
            "Car Rental Facility"
        ],
        "Internet": [
            "Free WiFi",
            "Wi-Fi in all rooms",
            "Wi-Fi"
        ],
        "Services and Conveniences": [
            "Travel Desk",
            "Concierge Services",
            "Currency Exchange",
            "Daily Housekeeping",
            "Dry Cleaning Service",
            "Laundry",
            "Luggage Storage",
            "Smoking Area",
            "Hot Shower"
        ]
    }



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
    amenities =models.JSONField(default=default_amenities)
    cleaniless_rate = models.FloatField(default=3.8)
    service_rate = models.FloatField(default=3.9)
    comfort_rate = models.FloatField(default=3.6)
    amenities_rate = models.FloatField(default=3.7)
    def __str__(self):
        return self.name
class HotelImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE,related_name="hotel_images")
    image=models.ImageField(upload_to="hotel_images")


class RoomCategory(models.Model):
    name=models.CharField(max_length=150,unique=True)

    def __str__(self) -> str:
        return f"{self.name}"
    
def get_amentiy_room():
    return {
        "amentiy_room": ["King size Bed", "Air Conditioning ", "Room Service", "High-speed Internet Access (Wi-Fi/Wired)", "Flat-screen TV with Cable/Satellite Channels"]
    }
class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE,related_name="rooms_type")
    rnm = models.CharField("room name",max_length=255)
    meal_plan = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    amenity = models.JSONField(null=True)
    category = models.ForeignKey(RoomCategory,on_delete=models.CASCADE,related_name="cate_roomtype")


    def __str__(self):
        return f"{self.rnm} - {self.hotel.name}"


class HotelDetails(models.Model):
    package = models.ForeignKey('CustomisedPackage', on_delete=models.CASCADE, related_name='hotel_details')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE,null=True)
    citynight= models.ForeignKey(CityNight, on_delete=models.CASCADE,null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    room_type=models.CharField(max_length=40,null=True)
    room=models.ForeignKey(RoomType, null=True,on_delete=models.CASCADE)
    meal_plans=models.CharField(max_length=100,null=True)
    facilities=MultiSelectField(null=True,blank=True)
    number_of_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
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
    age_limit = models.CharField(max_length=30,null=True, blank=True)
    activity_name = models.CharField(max_length=350)
    sequence=models.IntegerField(null=True, blank=True)
    activity_desc = models.TextField(null=True, blank=True)
    activity_city = models.ForeignKey(Cities, on_delete=models.CASCADE, related_name="activities_in_city",null=True)

    def __str__(self):
        return self.activity_name if self.activity_name else "Activity"




class Itinerary(models.Model):
    package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE,)
    citynight= models.ForeignKey(CityNight, on_delete=models.CASCADE,null=True)
    days=models.DateField()
    # activities=models.ManyToManyField(Activity,related_name="Itinrtary_activities",)
    activity_input=models.TextField(null=True,blank=True)
    statues_choices=[
      ("PENDING","PENDING"),
      ("COMPLETED","COMPLETED"),
    ]
    status=models.CharField(max_length=60,default="PENDING",choices=statues_choices)
  
    class Meta:
        get_latest_by = "days"


class ItineraryActivity(models.Model):
    itinerary=models.ForeignKey(Itinerary,on_delete=models.CASCADE,related_name="itinerary_activity")
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
    category = MultiSelectField(max_length=250, choices=category_choices,default='leisure')
    duration = models.CharField(max_length=30, null=True, blank=True)  
    age_limit = models.CharField(null=True, blank=True,max_length=30)
    activity_name = models.CharField(max_length=350)
    sequence=models.IntegerField(null=True, blank=True)
    activity_desc = models.TextField(null=True, blank=True)
    activity_city = models.ForeignKey(Cities, on_delete=models.CASCADE, related_name="itiner_acti_city",null=True)



class ExpenseDetail(BaseModel):
    package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE)
    vendor= models.CharField(max_length=50)
    date=models.DateField()
    tax=models.IntegerField()
    company=models.ForeignKey(Company, on_delete=models.CASCADE)
    purposes=models.TextField()
    amount=models.DecimalField(decimal_places=2,max_digits=20)
    total_amount=models.DecimalField(decimal_places=2,max_digits=20)
    # date,amount,tax,purpose,total amt

    def __str__(self) -> str:
        return f"{self.vendor}"
    
# invoice tables 
class InvoiceMaster(BaseModel):

    invoice_no = models.CharField(max_length=50) #FORMAT AUTO GENERATE IN SEQUENCE INV240001 
    invoice_type=models.CharField(max_length=100)
    company=models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE,null=True,blank=True)
    invoice_date = models.DateField()
    tax_amt= models.DecimalField(max_digits=10, decimal_places=2,default=0)
    discount_amt = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    gross_amt = models.DecimalField(max_digits=10, decimal_places=2)
    net_amt = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    narration = models.TextField(blank=True, null=True)

class AirTicketInvoice(BaseModel):
    # INV TPYE
    NORMAL='Normal'
    REISSUE='Reissue'
    VOID='VOID'
    INV_TYPE_CHOICE=[
        (NORMAL,NORMAL),
        (REISSUE,REISSUE),
        (VOID,VOID)
    ]
   
    package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE,null=True,blank=True)
    company=models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    invoice_no = models.CharField(max_length=50) #FORMAT AUTO GENERATE IN SEQUENCE INV240001 
    invoice_type=models.CharField(max_length=100,choices=INV_TYPE_CHOICE,default=NORMAL)
    customer=models.ForeignKey(Customer, on_delete=models.CASCADE)
    # auto set customer state
    place_of_supply=models.CharField(max_length=150,null=True, blank=True)
    gov_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tds_amt = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amt = models.DecimalField(max_digits=10, decimal_places=2)
    net_amt = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amt = models.DecimalField(max_digits=10, decimal_places=2,default=0)
   
    invoice_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    narration = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_no}"

class AirTicketPassenger(models.Model):
    invoice = models.ForeignKey(AirTicketInvoice, related_name='passengers', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254,null=True, blank=True)
    phone = models.CharField(max_length=20,null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    airline_name = models.CharField(max_length=100)
    flight_no=models.CharField(max_length=100,null=True)
    ticket_no=models.CharField(max_length=150,null=True,blank=True)
    departure_city = models.ForeignKey(Cities,on_delete=models.CASCADE,related_name='inv_departure_city')
    arrival_city =  models.ForeignKey(Cities,on_delete=models.CASCADE,related_name='inv_arrival_city')
    # departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    flight_class = models.CharField(max_length=20, choices=[
        ('Economy', 'Economy'),
        ('Business', 'Business'),
        ('First Class', 'First Class'),
    ])
    pnr_no = models.CharField(max_length=20)
    # change 
    basic_amt =models.DecimalField(decimal_places=2,max_digits=50)
    yq_tax=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    yr_tax=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    k3_tax=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    other_tax=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    other_change=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    # markup 
    markup_basic=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    markup_yq=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    markup_other=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    gross_total=models.DecimalField(decimal_places=2,max_digits=50,default=0)
    def __str__(self):
        return f"{self.name}"