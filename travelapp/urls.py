from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #login
    path('user_login/', views.user_login,name='user_login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('companies/', views.view_all_companies, name='view_all_companies'),
    path('companies/create/', views.create_company, name='create_company'),
    path('companies/<int:pk>/update/', views.update_company, name='update_company'),
    path('companies/<int:pk>/delete/', views.delete_company, name='delete_company'),

     # Customer URLs
    path('customers/', views.view_all_customers, name='view_all_customers'),
    path('customers/create/', views.create_customer, name='create_customer'),
    path('customers/<int:pk>/update/', views.update_customer, name='update_customer'),
    path('customers/<int:pk>/delete/', views.delete_customer, name='delete_customer'),

    # Package URLs
    path('packages/', views.view_all_packages, name='view_all_packages'),
    path('packages/create/', views.create_package, name='create_package'),
    path('packages/<int:pk>/update/', views.update_package, name='update_package'),
    path('packages/<int:pk>/delete/', views.delete_package, name='delete_package'),

    #employee 
    path('add_employee/',views.add_employee),
    
    path("add_employee_attendance/<int:employee_id>/",views.add_employee_attendance),

    path("create_custom_package/",views.create_custom_package),
    path("update_custom_package/<int:pk>/",views.update_custom_package),
    path("delete_custom_package/<int:pk>/",views.delete_custom_package),

    path("add_travel_details/",views.add_travel_details),
    path("update_travel_details/<int:pk>/",views.update_travel_details),
    path("delete_travel_details/<int:pk>/",views.delete_travel_details),

    path("add_activity/",views.add_activity),
    path("update_activity/<int:pk>/",views.update_activity),
    path("delete_activity/<int:pk>/",views.delete_activity),

    path("get_itinerary/<int:pk>/",views.get_itinerary),
    path("add_itinerary/<int:package_id>/",views.add_itinerary),
    path("add_itinerary_activity/<int:pk>/",views.add_itinerary_activity),

    path("forgot_password/",views.forgot_password),
    path("change_password/",views.change_password),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
