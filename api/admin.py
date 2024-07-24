from django.contrib import admin
from .models import *
# Register your models here.

class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1  # Number of empty room types to display
class HotelImgsInline(admin.StackedInline):
    model = HotelImages
    extra = 1  # Number of empty room types to display

class ItineraryActivityInline(admin.TabularInline):
    model = ItineraryActivity
    extra = 1 # Number of empty 

class ItineraryAdmin(admin.ModelAdmin):
    inlines = [ItineraryActivityInline]


class HotelAdmin(admin.ModelAdmin):
    inlines = [RoomTypeInline,HotelImgsInline]
    search_fields=['name','city__name']
    list_display=['name','city','star_rating',]
    list_filter=['name','city__name','star_rating']

admin.site.register(Hotel,HotelAdmin)   

admin.site.register(Country)
admin.site.register(RoomCategory)
admin.site.register(RoadTransportOption)

class CitiesAdmin(admin.ModelAdmin):
    list_filter = ('name','country__name', 'state__name')  # Add fields you want to filter by
    search_fields = ('name', 'country__name', 'state__name')  # Add fields you want to search in

admin.site.register(Company)
admin.site.register(Customer)
admin.site.register(Package)
admin.site.register(Employee)
admin.site.register(Cities,CitiesAdmin)
admin.site.register(Nationality)
admin.site.register(CustomisedPackage)
admin.site.register(Travel_Details)
admin.site.register(Activity)
admin.site.register(EmployeeAttendance)
admin.site.register(CityNight)
admin.site.register(Itinerary,ItineraryAdmin)