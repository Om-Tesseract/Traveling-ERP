from django.urls import path
from api import views
urlpatterns = [
    path('employee/',views.EmployeeListCreateView.as_view(),name="EmployeeListCreateView"),
    path('employee/<int:pk>/',views.EmployeeUpdateDeleteView.as_view(),name="EmployeeUpdateDeleteView"),
    path('customers/',views.CustomerListCreateView.as_view(),name="CustomerListCreateView"),
    path('customers/<int:pk>/',views.CustomerUpdateDeleteView.as_view(),name="CustomerUpdateDeleteView"),
    path('countries_data_entry/',views.countries_data_entry,name="CountriesDataEntry"),
    path('states_data_entry/',views.states_data_entry,name="StatesDataEntry"),
    path('cities_data_entry/',views.city_data_entry,name="CitiesDataEntry"),
    path('countries/',views.CountriesListView.as_view(),name="CountriesList"),
    path('states/<int:country_id>/',views.StatesListView.as_view(),name="StatesListView"),
    path('city/<int:state_id>/',views.CitiesListView.as_view(),name="CitiesListView"),
]
