from django.contrib import admin
from .models import *
# Register your models here.

class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1  # Number of empty room types to display

class HotelAdmin(admin.ModelAdmin):
    inlines = [RoomTypeInline]

admin.site.register(Hotel,HotelAdmin)   

admin.site.register(Country)
admin.site.register(RoadTransportOption)