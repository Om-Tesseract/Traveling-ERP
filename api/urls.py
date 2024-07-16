from django.urls import path
from api import views
urlpatterns = [
    # employees urls
    path('employee/',views.EmployeeListCreateView.as_view(),name="EmployeeListCreateView"),
    path('employee/<int:pk>/',views.EmployeeUpdateDeleteView.as_view(),name="EmployeeUpdateDeleteView"),
    path('employee/attendant/',views.EmployeeAttendanceListCreateAPI.as_view(),name="EmployeeAttendanceListCreateAPI"),
    # activity urls
    path('activity/',views.ActivityListCreateAPI.as_view(),name="ActivityListCreateAPI"),
    path('activity/<int:pk>/',views.ActivityUpdateDestroyAPI.as_view(),name="ActivityUpdateDestroyAPI"),

    # customized packages create or update only packages
    path("customized_package/", views.CustomizedPackageListCreateAPI.as_view(), name="CustomizedPackageListCreateAPI") ,
    path("customized_package/<int:pk>/", views.CustomizedPackageUpdateDestroyAPI.as_view(), name="CustomizedPackageUpdateDestroyAPI") ,
    # list of customized packages
    path('customized_package/itinerary/',views.CustomizePackageListView.as_view(), name="ItineraryPackageGetView"),
    path('customized_package/itinerary/<int:package_id>/',views.CustomizePackageListView.as_view(), name="ItineraryPackageListView"),
    path('customized_package/update/<int:pk>/',views.UpdateCustomisedPackageView.as_view(), name="UpdateCustomisedPackageView"),
  

    path('itinerary/<int:pk>/',views.ItineraryUpdateDeleteView.as_view(),name="ItineraryUpdateDeleteView"),
    # Travel_Details
    path('travel_details/', views.TravelDetailsListCreateAPI.as_view(), name="TravelDetailsListCreateAPI"),
    path('travel_details/<int:pk>/', views.TravelDetailsUpdateDestroyAPI.as_view(), name="TravelDetailsUpdateDestroy"),


    #road Transport api
    path('road_transport/',views.RoadTransportListCreateView.as_view(), name="RoadTransportListCreate"),
    path('road_transport/<int:pk>/', views.RoadTransportRetrieveUpdateDestroyView.as_view(), name="RoadTransportRetrieveUpdate"),

    path("roomtypelist/", views.RoomTypeListView, name="RoomTypeListView"),
    # hotel 
    path('hotel',views.HotelListCreateView.as_view(), name="HotelListCreate"),
    path('hotel/<int:pk>/',views.HotelRetrieveUpdateDestroyAPIView.as_view(), name="HotelRetrieveUpdate"),
   
    # customers urls 
    path('customers/',views.CustomerListCreateView.as_view(),name="CustomerListCreateView"),
    path('customers/<int:pk>/',views.CustomerUpdateDeleteView.as_view(),name="CustomerUpdateDeleteView"),
   
   # country and state and cities urls
    path('countries/',views.CountriesListView.as_view(),name="CountriesList"),
    path('states/<int:country_id>/',views.StatesListView.as_view(),name="StatesListView"),
    path('city/<int:state_id>/',views.CitiesListView.as_view(),name="CitiesListView"),
    path('city/<str:search>/',views.CitiesListView.as_view(),name="CitiesSearchListView"),
    path('city/',views.CitiesListView.as_view(),name="CitiesSearchListView"),
    # data entry 
    path('countries_data_entry/',views.countries_data_entry,name="CountriesDataEntry"),
    path('states_data_entry/',views.states_data_entry,name="StatesDataEntry"),
    path('cities_data_entry/',views.city_data_entry,name="CitiesDataEntry"),
    path('hotel_data_entry/',views.hotel_data_entry,name="hotel_data_entry"),
    path('rt_data_entry/',views.rt_data_entry,name="rt_data_entry"),
    
]
