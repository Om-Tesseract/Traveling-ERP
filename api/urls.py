from django.urls import path
from api import views
urlpatterns = [
    # employees urls
    path('dashboard/',views.DashboardListView.as_view(),name="DashboardViews"),
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
    

    path('itinerary/<int:pk>/swap/',views.ItineraryChangeDayView.as_view(),name="ItineraryChangeDayView"),
    # Travel_Details
    path('travel_details/', views.TravelDetailsListCreateAPI.as_view(), name="TravelDetailsListCreateAPI"),
    path('travel_details/<int:pk>/', views.TravelDetailsUpdateDestroyAPI.as_view(), name="TravelDetailsUpdateDestroy"),

    path('hotel_details/<int:pk>/', views.HotelDetailsUpdateView.as_view(), name="HotelDetailsUpdateView"),
    
    #AirTicketInvoice
    path("air_ticket_invoice/", views.AirTicketInvoiceListCreateView.as_view(), name="AirTicketInvoiceListCreate"),
    path("air_ticket_invoice/<int:pk>/", views.AirTicketInvoiceRetrieveUpdateDestroyAPIView.as_view(), name="AirTicketInvoiceRetrieveUpdateDestroyAPIView"),

    # path("summary/<int:package_id>/",views.SummaryTripApi.as_view(), name="SummaryView"),
    #road Transport api
    path('road_transport/',views.RoadTransportListCreateView.as_view(), name="RoadTransportListCreate"),
    path('road_transport/<int:pk>/', views.RoadTransportRetrieveUpdateDestroyView.as_view(), name="RoadTransportRetrieveUpdate"),

    path("roomtypelist/", views.RoomTypeListView, name="RoomTypeListView"),
    path("mealplanlist/", views.MealPlanListView, name="MealPlanListView"),
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
    path('city/<int:pk>/',views.CitiesListView.as_view(),name="CitiesSearchListView"),
    path('city/update_delete/<int:pk>/',views.CitiesUpdateDestroyView.as_view(),name="CitiesUpdateDestroyView"),
    # data entry 
    path('activity_data_entry/',views.activity_data_entry,name="CountriesDataEntry"),
    path('countries_data_entry/',views.countries_data_entry,name="CountriesDataEntry"),
    path('states_data_entry/',views.states_data_entry,name="StatesDataEntry"),
    path('cities_data_entry/',views.city_data_entry,name="CitiesDataEntry"),
    path('hotel_data_entry/',views.hotel_data_entry,name="hotel_data_entry"),
    path('rt_data_entry/',views.rt_data_entry,name="rt_data_entry"),
 
    path('companies/', views.view_all_companies, name='view_all_companies'),
    path('companies/create/', views.create_company, name='create_company'),
    path('companies/<int:pk>/update/', views.update_company, name='update_company'),
    path('companies/<int:pk>/delete/', views.delete_company, name='delete_company'),

    path('contact/create/', views.ContactCreateView.as_view(), name="create_contact"),
    path('contact/list/',views.ContactListView.as_view(), name="list_contact"),
    path('contact/<int:pk>/',views.ContactUpdateDeleteView.as_view(),name="update_contact"),

    path('flightsdata/',views.FlightsDataApi.as_view(),name="flight"),

    
    # Expanse api
    path('expense/',views.ExpanseListCreateView.as_view(), name="ExpanseListCreateView"),
    path('expense/<int:pk>/',views.ExpanseRetrieveUpdateDestroyAPIView.as_view(), name="ExpanseRetrieveUpdateDestroyAPIView"),
    
    # Invoice Api   
    path('invoice/',views.InvoiceListCreateAPI.as_view(),name="InvoiceListCreate"),
    path('invoice/<int:pk>/',views.InvoiceUpdateDestroyAPI.as_view(),name="InvoiceUpdateDestroy"),
    
    # payment receipt
    path('payment_receipt/',views.PaymentReceiptListCreateAPI.as_view(),name="PaymentReceiptListCreate"),
    path('payment_receipt/<int:pk>/',views.PaymentReceiptUpdateDestroyAPI.as_view(),name="PaymentReceiptUpdateDestroy")

]
