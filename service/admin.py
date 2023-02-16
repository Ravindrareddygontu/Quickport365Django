from django.contrib import admin
from .models import ParcelDetails, OrderDetails, Drivers_orders, Admin_driver
from django.contrib.auth.models import User


@admin.register(ParcelDetails)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_weight', 'item_name', 'pickup_date', 'parcel_image']


@admin.register(OrderDetails)
class OrderDetailsadmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'origin', 'destination',
                    'date', 'price', 'status', 'picked']


@admin.register(Drivers_orders)
class DriversAdmin(admin.ModelAdmin):
    list_display = ['driver', 'order']


@admin.register(Admin_driver)
class Admin_driveradmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone',
                    'govt_id', 'id_type', 'flag']