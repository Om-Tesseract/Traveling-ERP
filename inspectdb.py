# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApiActivity(models.Model):
    category = models.CharField(max_length=250)
    duration = models.CharField(max_length=30, blank=True, null=True)
    age_limit = models.IntegerField(blank=True, null=True)
    activity_name = models.CharField(max_length=350)
    activity_desc = models.TextField(blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)
    activity_city = models.ForeignKey('ApiCities', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_activity'


class ApiAirticketinvoice(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    is_active = models.BooleanField()
    invoice_no = models.CharField(max_length=50)
    invoice_type = models.CharField(max_length=100)
    place_of_supply = models.CharField(max_length=150, blank=True, null=True)
    gov_tax = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    tds_amt = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    gross_amt = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    net_amt = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    discount_amt = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    notes = models.TextField(blank=True, null=True)
    narration = models.TextField(blank=True, null=True)
    company = models.ForeignKey('ApiCompany', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, blank=True, null=True)
    customer = models.ForeignKey('ApiCustomer', models.DO_NOTHING)
    package = models.ForeignKey('ApiCustomisedpackage', models.DO_NOTHING, blank=True, null=True)
    updated_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, related_name='apiairticketinvoice_updated_by_set', blank=True, null=True)
    invoice_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'api_airticketinvoice'


class ApiAirticketpassenger(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    airline_name = models.CharField(max_length=100)
    flight_no = models.CharField(max_length=100, blank=True, null=True)
    ticket_no = models.CharField(max_length=150, blank=True, null=True)
    arrival_date = models.DateTimeField()
    flight_class = models.CharField(max_length=20)
    pnr_no = models.CharField(max_length=20)
    basic_amt = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    yq_tax = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    yr_tax = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    k3_tax = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    other_tax = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    other_change = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    arrival_city = models.ForeignKey('ApiCities', models.DO_NOTHING)
    departure_city = models.ForeignKey('ApiCities', models.DO_NOTHING, related_name='apiairticketpassenger_departure_city_set')
    invoice = models.ForeignKey(ApiAirticketinvoice, models.DO_NOTHING)
    markup_basic = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    markup_other = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    markup_yq = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    gross_total = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'api_airticketpassenger'


class ApiCities(models.Model):
    country = models.ForeignKey('ApiCountry', models.DO_NOTHING)
    state = models.ForeignKey('ApiStates', models.DO_NOTHING)
    name = models.CharField(max_length=60)
    img = models.CharField(max_length=100, blank=True, null=True)
    img_url = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_cities'


class ApiCitynight(models.Model):
    nights = models.IntegerField()
    package = models.ForeignKey('ApiCustomisedpackage', models.DO_NOTHING)
    city = models.ForeignKey(ApiCities, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_citynight'


class ApiCompany(models.Model):
    website = models.CharField(max_length=50, blank=True, null=True)
    heading_logo = models.CharField(max_length=100, blank=True, null=True)
    company_logo = models.CharField(max_length=100, blank=True, null=True)
    primary_color = models.CharField(max_length=100, blank=True, null=True)
    secondary_color = models.CharField(max_length=100, blank=True, null=True)
    custom_user = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, blank=True, null=True)
    primary_txt_color = models.CharField(max_length=60, blank=True, null=True)
    secondary_txt_color = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_company'


class ApiCountry(models.Model):
    name = models.CharField(unique=True, max_length=50)
    iso3 = models.CharField(max_length=30, blank=True, null=True)
    iso2 = models.CharField(max_length=30, blank=True, null=True)
    numeric_code = models.CharField(max_length=20, blank=True, null=True)
    phone_code = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    currency_name = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    emojiu = models.CharField(db_column='emojiU', max_length=50, blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(max_length=50, blank=True, null=True)
    currency_symbol = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_country'


class ApiCustomer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=15)
    country = models.ForeignKey(ApiCountry, models.DO_NOTHING, blank=True, null=True)
    city = models.ForeignKey(ApiCities, models.DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(ApiCompany, models.DO_NOTHING, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    state = models.ForeignKey('ApiStates', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_customer'


class ApiCustomisedpackage(models.Model):
    leaving_on = models.DateTimeField()
    number_of_rooms = models.IntegerField()
    number_of_adults = models.IntegerField()
    number_of_children = models.IntegerField()
    interests = models.CharField(max_length=200, blank=True, null=True)
    who_is_travelling = models.CharField(max_length=50, blank=True, null=True)
    pregnant_women = models.BooleanField()
    elderly_people = models.BooleanField()
    with_walking_difficulty = models.BooleanField()
    teenager = models.BooleanField()
    women_only = models.BooleanField()
    men_only = models.BooleanField()
    star_rating = models.IntegerField()
    add_transfers = models.BooleanField()
    add_tours_and_travels = models.BooleanField()
    itinerary_created = models.BooleanField()
    customer = models.ForeignKey(ApiCustomer, models.DO_NOTHING, blank=True, null=True)
    leaving_from = models.ForeignKey(ApiCities, models.DO_NOTHING, blank=True, null=True)
    nationality = models.ForeignKey(ApiCountry, models.DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(ApiCompany, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    created_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField()
    is_deleted = models.BooleanField()
    updated_at = models.DateTimeField()
    updated_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, related_name='apicustomisedpackage_updated_by_set', blank=True, null=True)
    room_type = models.CharField(max_length=20, blank=True, null=True)
    package_name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'api_customisedpackage'


class ApiEmployee(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    is_active = models.BooleanField()
    emp_name = models.CharField(max_length=100)
    emp_department = models.CharField(max_length=100, blank=True, null=True)
    emp_dob = models.DateField(blank=True, null=True)
    company = models.ForeignKey(ApiCompany, models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, blank=True, null=True)
    emp_user = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, related_name='apiemployee_emp_user_set', blank=True, null=True)
    updated_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, related_name='apiemployee_updated_by_set', blank=True, null=True)
    emp_salary = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'api_employee'


class ApiEmployeeattendance(models.Model):
    date_of_attendance = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50)
    employee = models.ForeignKey(ApiEmployee, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_employeeattendance'


class ApiExpensedetail(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    is_active = models.BooleanField()
    vendor = models.CharField(max_length=50)
    date = models.DateField()
    tax = models.IntegerField()
    purposes = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    company = models.ForeignKey(ApiCompany, models.DO_NOTHING)
    created_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, blank=True, null=True)
    package = models.ForeignKey(ApiCustomisedpackage, models.DO_NOTHING)
    updated_by = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, related_name='apiexpensedetail_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_expensedetail'


class ApiFlightDetails(models.Model):
    depart_on = models.DateField()
    return_on = models.DateField(blank=True, null=True)
    flt_class = models.CharField(max_length=50)
    destination_to = models.ForeignKey(ApiCities, models.DO_NOTHING)
    package = models.ForeignKey(ApiCustomisedpackage, models.DO_NOTHING, blank=True, null=True)
    pickup_from = models.ForeignKey(ApiCities, models.DO_NOTHING, related_name='apiflightdetails_pickup_from_set')
    ret_destination_to = models.ForeignKey(ApiCities, models.DO_NOTHING, related_name='apiflightdetails_ret_destination_to_set', blank=True, null=True)
    ret_pickup_from = models.ForeignKey(ApiCities, models.DO_NOTHING, related_name='apiflightdetails_ret_pickup_from_set', blank=True, null=True)
    pnr = models.CharField(db_column='PNR', max_length=100, blank=True, null=True)  # Field name made lowercase.
    airlines = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=30)
    sequence = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'api_flight_details'


class ApiHotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    contact_info = models.JSONField(blank=True, null=True)
    city = models.ForeignKey(ApiCities, models.DO_NOTHING)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    rate = models.CharField(max_length=20, blank=True, null=True)
    ln = models.FloatField(blank=True, null=True)
    lt = models.FloatField(blank=True, null=True)
    star_rating = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_hotel'


class ApiHoteldetails(models.Model):
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    room_type = models.CharField(max_length=100)
    number_of_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    additional_requests = models.TextField(blank=True, null=True)
    hotel = models.ForeignKey(ApiHotel, models.DO_NOTHING)
    package = models.ForeignKey(ApiCustomisedpackage, models.DO_NOTHING)
    citynight = models.ForeignKey(ApiCitynight, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_hoteldetails'


class ApiItinerary(models.Model):
    days = models.DateField()
    activity_input = models.TextField(blank=True, null=True)
    package = models.ForeignKey(ApiCustomisedpackage, models.DO_NOTHING)
    status = models.CharField(max_length=60)
    citynight = models.ForeignKey(ApiCitynight, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_itinerary'


class ApiItineraryActivities(models.Model):
    itinerary = models.ForeignKey(ApiItinerary, models.DO_NOTHING)
    activity = models.ForeignKey(ApiActivity, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_itinerary_activities'
        unique_together = (('itinerary', 'activity'),)


class ApiNationality(models.Model):
    nationality_choice = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_nationality'


class ApiPackage(models.Model):
    package_name = models.CharField(max_length=100, blank=True, null=True)
    package_location = models.CharField(max_length=100, blank=True, null=True)
    number_of_persons = models.JSONField(blank=True, null=True)
    package_link = models.CharField(max_length=200, blank=True, null=True)
    custom_user = models.ForeignKey('AuthenticationCustomuser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_package'


class ApiRoadtransportoption(models.Model):
    vehicle_type = models.CharField(max_length=100)
    seats = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'api_roadtransportoption'


class ApiRoomtype(models.Model):
    rnm = models.CharField(max_length=255)
    meal_plan = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    availability = models.BooleanField()
    hotel = models.ForeignKey(ApiHotel, models.DO_NOTHING)
    amenity = models.TextField()

    class Meta:
        managed = False
        db_table = 'api_roomtype'


class ApiStates(models.Model):
    state_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.ForeignKey(ApiCountry, models.DO_NOTHING)
    name = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'api_states'


class ApiTravelDetails(models.Model):
    pnr = models.CharField(db_column='PNR', max_length=100, blank=True, null=True)  # Field name made lowercase.
    package = models.ForeignKey(ApiCustomisedpackage, models.DO_NOTHING, blank=True, null=True)
    road_transport = models.ForeignKey(ApiRoadtransportoption, models.DO_NOTHING, blank=True, null=True)
    destination = models.ForeignKey(ApiCities, models.DO_NOTHING, blank=True, null=True)
    pickup_from = models.ForeignKey(ApiCities, models.DO_NOTHING, related_name='apitraveldetails_pickup_from_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_travel_details'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthenticationCustomuser(models.Model):
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    username = models.CharField(unique=True, max_length=100, blank=True, null=True)
    password = models.CharField(max_length=500, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=10, blank=True, null=True)
    address1 = models.CharField(max_length=125, blank=True, null=True)
    address2 = models.CharField(max_length=125, blank=True, null=True)
    email = models.CharField(unique=True, max_length=254, blank=True, null=True)
    role = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'authentication_customuser'


class AuthenticationCustomuserGroups(models.Model):
    customuser = models.ForeignKey(AuthenticationCustomuser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authentication_customuser_groups'
        unique_together = (('customuser', 'group'),)


class AuthenticationCustomuserUserPermissions(models.Model):
    customuser = models.ForeignKey(AuthenticationCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authentication_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class TravelappTemptokenmodel(models.Model):
    email = models.CharField(max_length=50)
    token = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'travelapp_temptokenmodel'
