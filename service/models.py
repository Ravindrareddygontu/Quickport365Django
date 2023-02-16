from django.db import models
from django.contrib.auth.models import User, AbstractUser


class ParcelDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, null=True)
    item_weight = models.IntegerField()
    item_name = models.CharField(max_length=200)
    pickup_date = models.DateField(null=True)
    parcel_image = models.ImageField(upload_to='images')
    receiver_name = models.CharField(max_length=200, null=True)
    receiver_phone = models.CharField(max_length=12, null=True)
    created = models.DateTimeField(auto_now=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)


id_type = (('Aadhar_no', 'Aadhar no'),
        ('Driving_license', 'Driving license'),
        ('Pancard', 'Pancard'),
    )
class Admin_driver(models.Model):
    name = models.CharField(max_length=12, null=True, unique=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=120, null=True)
    address = models.CharField(max_length=120, null=True)
    id_type = models.CharField(max_length=20, choices=id_type, null=True)
    govt_id = models.CharField(max_length=12, null=True)
    temp_password = models.CharField(max_length=12, null=True)
    new_password = models.CharField(max_length=30, null=True)
    flag = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


ch = (("started", 'started'), ("in_process", 'in_process'), ("completed", 'completed'))


class OrderDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, editable=False)
    origin = models.IntegerField()
    destination = models.IntegerField()
    Destination_country = models.CharField(max_length=100, null=True, editable=False)
    item_weight = models.IntegerField()
    item_name = models.CharField(max_length=200)
    services = models.CharField(max_length=200)
    date = models.DateField(null=True)
    image = models.ImageField(null=True, editable=False)
    price = models.IntegerField(null=True)
    status = models.CharField(max_length=200, choices=ch, null=True, default='pending')
    picked = models.BooleanField(null=True)
    pickup_address = models.CharField(max_length=500, null=True)
    delivery_address = models.CharField(max_length=500, null=True)
    receiver_name = models.CharField(max_length=200, null=True)
    receiver_phone = models.CharField(max_length=200, null=True)
    driver = models.ForeignKey(Admin_driver, on_delete=models.SET_NULL, null=True)
    driver_phone = models.CharField(max_length=11, null=True)
    created = models.DateTimeField(auto_now=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, editable=False)
    booking_id = models.IntegerField()
    issue = models.TextField()
    created = models.DateTimeField(auto_now=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)


class Drivers_orders(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)













