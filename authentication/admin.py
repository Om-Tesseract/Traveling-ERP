from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class CustomUserAdmin(UserAdmin):
    # Define the fields to be displayed in the list view
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role')

    # Define the fields to be used in the form when adding or editing users
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'nick_name', 'email', 'mobile_number', 'address1', 'address2')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )

    # Define the fields to be used in the form when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'nick_name', 'email', 'mobile_number', 'address1', 'address2', 'role')}
        ),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('first_name',)

admin.site.register(models.CustomUser, CustomUserAdmin)