from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api import models
class CitiesAdmin(admin.ModelAdmin):
    list_filter = ('name','country__name', 'state__name')  # Add fields you want to filter by
    search_fields = ('name', 'country__name', 'state__name')  # Add fields you want to search in

admin.site.register(models.Company)
admin.site.register(models.Customer)
admin.site.register(models.Package)
admin.site.register(models.Employee)
admin.site.register(models.Cities,CitiesAdmin)
admin.site.register(models.Nationality)
admin.site.register(models.CustomisedPackage)
admin.site.register(models.Travel_Details)
admin.site.register(models.Activity)
admin.site.register(models.EmployeeAttendance)
admin.site.register(models.CityNight)
admin.site.register(models.Itinerary)
# admin.site.register(models.TempTokenModel)