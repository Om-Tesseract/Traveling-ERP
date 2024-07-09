from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api import models

admin.site.register(models.Company)
admin.site.register(models.Customer)
admin.site.register(models.Package)
admin.site.register(models.Employee)
admin.site.register(models.City)
admin.site.register(models.Nationality)
admin.site.register(models.CustomisedPackage)
admin.site.register(models.Travel_Details)
admin.site.register(models.Activity)
admin.site.register(models.EmployeeAttendance)
admin.site.register(models.CityNight)
admin.site.register(models.Itinerary)
# admin.site.register(models.TempTokenModel)