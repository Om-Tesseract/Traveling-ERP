from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from django.contrib.auth import authenticate,get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from api.models import Company
from django.contrib.auth.hashers import check_password,make_password
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.encoding import  smart_str ,force_bytes,force_str
from django.conf import settings
from .models import *
from django.template.loader import render_to_string
from .utils import send_email
class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # auth= get_user_model().objects.get(id=user.id)
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        get_user_model().objects.filter(id=user.id).update(last_login=timezone.now())
        
         
        return token
    def validate(self, attrs):
        credentials = {
            get_user_model().USERNAME_FIELD: attrs.get(get_user_model().USERNAME_FIELD),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user =authenticate(
                self.context['request'],
                username=credentials[get_user_model().USERNAME_FIELD],
                password=credentials['password']
            )
            if user:
                refresh = self.get_token(user)
                company_object = Company.objects.filter(custom_user=user).first()
        
                # Assuming 'company' field in CustomUser is a ForeignKey to the Company model
                company_logo = company_object.company_logo if company_object else None
                    # Generate tokens
                access_token = AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                data = {
                 'message': 'Login Successful',
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
            'role': user.role,
            'id': user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            'company_logo': str(company_logo) if company_logo else None,
            'heading_logo': str(company_object.heading_logo) if company_object and company_object.heading_logo else None,
            'primary_color': company_object.primary_color if company_object else None,
            'secondary_color': company_object.secondary_color if company_object else None,
            'secondary_txt_color': company_object.secondary_txt_color if company_object else None,
            'primary_txt_color': company_object.primary_txt_color if company_object else None,
                }
               
                return data
            else:
                if get_user_model().objects.filter(email= credentials[get_user_model().USERNAME_FIELD]).exists():
                    msg="Password is incorrect, please try again or you can click on forget Password."
                else:
                    msg="This email is not registered, please sign up."

               
                raise serializers.ValidationError({"error":msg})

        else:
            msg = '"username" and "password" are required.'
            raise serializers.ValidationError({"error":msg})
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True,'required': True},
                        'email':{
                            "required": True
                        },
                        'first_name':{
                            'required':True
                        },
                        'mobile_number':{
                            'required':True
                        },

                        }
        
    def validate(self, attrs):
        instance = self.instance  # Get the current instance being updated
      
        if instance is not None and attrs.get('email') is not None and str(instance.email).strip() == str(attrs.get('email')).strip():
            return super().validate(attrs)
        else:
            User = get_user_model()
            if User.objects.filter(email= attrs.get('email')).exists():
                raise serializers.ValidationError({"email": ["User with this email already exists."]})
                
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = get_user_model().objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance
    

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(min_length=2)
    class Meta:
        fields=['email']
    def validate(self,attrs):
            email= attrs.get('email','')
            print("email",email)
            if get_user_model().objects.filter(email=email).exists():
                user = get_user_model().objects.get(email=email)
                uid= urlsafe_base64_encode(force_bytes(user.id))
                print('Encode id:',uid)
                token=PasswordResetTokenGenerator().make_token(user)
                print("reset password Token:= ",token)
                if not settings.DEBUG:
                    link=f'{settings.HOST_URL}/auth/reset-password/'+uid+'/'+token+'/'
                else:
                    link=f'{settings.LOCALHOST}/auth/reset-password/'+uid+'/'+token+'/'
                print('reset password link :=',link)
                body='Click Following Link to Reset Your Password:'+link 
                data={
                    
                    'reset_link':link,
                    
                    'username':user.username,
                    'to_email':user.email,
                    'name':f"{user.first_name} {user.last_name}" ,
                    
                }
                subject="Reset Your Password"
                try:
                    template_render = render_to_string("email_base.html", data)

                    print(settings.EMAIL_HOST_USER)

                    email_data = {
                        "from_email": settings.EMAIL_HOST_USER,
                        "to_email": [email],
                        "subject":subject ,
                        "body": template_render,
                        "attachment": [],
                        "cc_email": "",
                        "bcc_email": "",
                    }
                    send_email(data=email_data)
                except Exception as e:

                    print('Error =>',e)
                    raise serializers.ValidationError({"error":"Send email failed"})
                return attrs
            else:
                raise serializers.ValidationError({"error":'This email is not registered, please sign up.'})
            

class UserPasswordResetViewSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')
        new_password = attrs.get('new_password')

        try:
            user_id= force_str(urlsafe_base64_decode(uid))
            user = get_user_model().objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise serializers.ValidationError({"error":'Invalid reset password link'})
    
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError({"error":'Invalid reset password link'})

        attrs['user'] = user
        attrs['new_password'] = new_password
        return attrs

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()

class UserChangePasswordSerializer(serializers.Serializer):
    currentpassword=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    newpassword=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['currentpassword','newpassword']
    def validate(self, attrs):
            currentpassword= attrs.get('currentpassword')
            newpassword=attrs.get('newpassword') 
            user=self.context.get('user')
            usercurrentpassword= user.password
            match_password=check_password(currentpassword,usercurrentpassword)
           
            if not match_password:
                raise serializers.ValidationError("Current Password is incorrect")
            
            
            user.set_password(newpassword)
            user.save()
            return attrs


class ProfileUserSerializer(serializers.ModelSerializer):
    website=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    heading_logo=serializers.ImageField(write_only=True,allow_null=True,required=False)
    company_logo= serializers.ImageField(write_only=True,allow_null=True,required=False)
    primary_color=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    primary_txt_color=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    secondary_color=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    secondary_txt_color=serializers.CharField(write_only=True,allow_null=True,allow_blank=True,required=False)
    
    class Meta:
        model=get_user_model()
        fields=['username','first_name',
                'last_name','email',
                'mobile_number','address1',
                'address2','nick_name',
                'website','heading_logo',
                'company_logo','primary_color','primary_txt_color',
                'secondary_color','secondary_txt_color'
                ]
        
    def validate(self, attrs):
        instance = self.instance  # Get the current instance being updated
      
        if instance is not None and attrs.get('email') is not None and str(instance.email).strip() == str(attrs.get('email')).strip():
            return super().validate(attrs)
        else:
            User = get_user_model()
            if User.objects.filter(email= attrs.get('email')).exists():
                raise serializers.ValidationError({"email": ["User with this email already exists."]})
                
        return super().validate(attrs)
    def to_representation(self, instance):
        data= super().to_representation(instance)
        req_user=self.context.get('request').user
        if req_user.role=="Company":
            company=Company.objects.filter(custom_user=req_user).values().first()
            company.pop('custom_user_id',None)
            company_id=company.pop('id',None)
            data['company_id']=company_id
            data.update(company)
        return data
    def update(self, instance, validated_data):
        req_user=self.context.get('request').user
        if req_user.role=="Company":

            company = Company.objects.filter(custom_user=req_user).first()
            if company:
                for field in ['website', 'heading_logo', 'company_logo', 'primary_color', 'primary_txt_color', 'secondary_color', 'secondary_txt_color']:
                    if field in validated_data:
                        setattr(company, field, validated_data.pop(field))
                company.save()
        return super().update(instance, validated_data)

