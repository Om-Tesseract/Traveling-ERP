from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from api.models import Company,Customer,Package,CustomUser,Employee,Travel_Details,CustomisedPackage,Activity,CityNight,Itinerary
from .serializers import CompanySerializer,CustomerSerializer,PackageSerializer,EmployeeSerializer,EmployeeAttendanceSerializer,CustomisedPackageSerializer,TravelDetailsSerializer,ActivitySerializer,ItinerarySerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.utils.html import strip_tags
import random,string
from django.template.loader import render_to_string
from django.conf import settings

def send_email(data):
    send_mail(subject=data.get("subject"),
            html_message=data.get("body"),
            from_email=data.get("from_email"),
            recipient_list=data.get("to_email"),
            fail_silently=True,
            message=strip_tags(data.get("body")))
    
    print("Email Sent !")

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email=request.data.get("email")
    print(email)
    if CustomUser.objects.filter(email=email).first()!=None:
    # if True:
        subject="Forgot Password"
        user=f"{CustomUser.objects.filter(email=email).first().first_name} {CustomUser.objects.filter(email=email).first().last_name}"

        random_number = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
  
        # if TempTokenModel.objects.filter(email=email).exists():
        #     random_number = TempTokenModel.objects.get(email=email).token
        # else:
        #     TempTokenModel.objects.create(email = email, token = random_number)

        template_render = render_to_string("email_base.html", {
            "html_subject": subject,
            "user":user,
            "reset_link": f"https://icams.co.in/resetPass/{random_number}"
        })

        print(settings.EMAIL_HOST_USER)

        email_data = {
            "from_email": settings.EMAIL_HOST_USER,
            "to_email": [email],
            "subject": subject,
            "body": template_render,
            "attachment": [],
            "cc_email": "",
            "bcc_email": "",
        }

        send_email(email_data)
        return Response({"message":"Email sent successfully!", "status":200})
    else:
        return Response({"message":"No user found with this email", "status":500})

@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request):
    password = request.data.get("password")
    token = request.data.get("token")

    # if TempTokenModel.objects.filter(token=token).exists():
    #     u = CustomUser.objects.get(email=TempTokenModel.objects.get(token=token).email)
    #     u.set_password(password)
    #     u.save()
    #     return Response({"message":"Password changed successfully!", "status":200})
    # else:
    return Response({"message":"No Token found", "status":500})


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)
    
    if user:
        company_object = Company.objects.filter(custom_user=user).first()
        
        # Assuming 'company' field in CustomUser is a ForeignKey to the Company model
        company_logo = company_object.company_logo if company_object else None
        
        # Generate tokens
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)

        response_data = {
            'message': 'Login Successful',
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
            'role': user.role,
            'id': user.id,
            'company_logo': str(company_logo) if company_logo else None,
            'heading_logo': str(company_object.heading_logo) if company_object and company_object.heading_logo else None,
            'primary_color': company_object.primary_color if company_object else None,
            'secondary_color': company_object.secondary_color if company_object else None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_companies(request):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
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
    
    serializer = CompanySerializer(data=data)
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
        serializer = CompanySerializer(company)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Customer Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_customers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method=="GET":
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Package Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_packages(request):
    packages = Package.objects.all()
    serializer = PackageSerializer(packages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_package(request):
    serializer = PackageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def update_package(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method=="GET":
        serializer = PackageSerializer(package)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = PackageSerializer(package, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_package(request, pk):
    package = get_object_or_404(Package, pk=pk)
    package.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def add_employee(request):
    role = request.user.role
    
    if request.method == "POST":
        if role == "Company" or role == "Admin":
            # Extract user-related data from the request
            user_data = {
                'email': request.data.get('email'),
                'password': request.data.get('password'),
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                'nick_name': request.data.get('nick_name'),
                'mobile_number': request.data.get('mobile_number'),
                'address1': request.data.get('address1'),
                'address2': request.data.get('address2'),
                'email': request.data.get('email'),
                'role': 'Employee',  # Set role as Employee
            }
            
            try:
                user = CustomUser.objects.create(**user_data)
                user.set_password(user_data['password'])
                user.save()
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            employee_data = request.data.copy()
            employee_data['employee_user'] = user.id
            employee_data['custom_user'] = user.id

            # Serialize and create the Employee
            serializer = EmployeeSerializer(data=employee_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Invalid request method or insufficient permissions'}, status=status.HTTP_400_BAD_REQUEST)


from datetime import datetime
@api_view(['POST'])
def add_employee_attendance(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    data['employee'] = employee.id
    data['date_of_attendance']=datetime.now()
    serializer = EmployeeAttendanceSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_custom_package(request):
    serializer = CustomisedPackageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def update_custom_package(request, pk):
    try:
        package = CustomisedPackage.objects.get(pk=pk)
    except CustomisedPackage.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CustomisedPackageSerializer(package, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_custom_package(request, pk):
    try:
        package = CustomisedPackage.objects.get(pk=pk)
    except CustomisedPackage.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)
    
    package.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def add_travel_details(request):
    serializer = TravelDetailsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def update_travel_details(request, pk):
    try:
        package = Travel_Details.objects.get(pk=pk)
    except Travel_Details.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TravelDetailsSerializer(package, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_travel_details(request, pk):
    try:
        package = Travel_Details.objects.get(pk=pk)
    except Travel_Details.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)
    
    package.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_activity(request):
    role = request.user.role
    print(role)
    if role=="Admin":
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_activity(request, pk):
    role = request.user.role
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'error': 'activity not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if role=="Admin":
        serializer = ActivitySerializer(activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_activity(request, pk):
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
    
    activity.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

import datetime

@api_view(['POST','GET'])
@permission_classes([AllowAny])
def add_itinerary(request,package_id):
    city_nights = CityNight.objects.filter(package_id=package_id)
    package = get_object_or_404(CustomisedPackage, id=package_id)
    travel_details=get_object_or_404(Travel_Details,package=package)
    leaving_date = package.leaving_on
    
    total_nights = sum(int(city_night.nights) for city_night in city_nights)

    itineraries=[]
    if package.itinerary_created==False:
        package.itinerary_created=True
        package.save()
        for i in range(total_nights):
            itinerary = Itinerary.objects.create(package=package, days=leaving_date + datetime.timedelta(days=i),travel_details=travel_details)
            itineraries.append(itinerary)
     
    return Response()


@api_view(['POST','GET'])
# @permission_classes([AllowAny])
def add_itinerary_activity(request,itinerary_id):
    role = request.user.role
    try:
        itinerary = Itinerary.objects.get(pk=itinerary_id)
    except Itinerary.DoesNotExist:
        return Response({'error': 'activity not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if role=="Admin":
        serializer = ItinerarySerializer(itinerary, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
def get_itinerary(request,pk):
   
   city_nights=CityNight.objects.filter(customer=pk)
   print(city_nights)
   return Response()

