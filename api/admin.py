from django.contrib import admin
from .models import *
# Register your models here.

class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1  # Number of empty room types to display
class HotelImgsInline(admin.TabularInline):
    model = HotelImages
    extra = 1  # Number of empty room types to display

class HotelAdmin(admin.ModelAdmin):
    inlines = [RoomTypeInline,HotelImgsInline]
    search_fields=['name','city__name']
    list_display=['name','city','star_rating',]
    list_filter=['name','city__name','star_rating']

admin.site.register(Hotel,HotelAdmin)   

admin.site.register(Country)
admin.site.register(RoomCategory)
admin.site.register(RoadTransportOption)