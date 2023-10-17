from django.db import models
from django.contrib.auth.models import User, AbstractUser
from phone_field import PhoneField
#from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

# Create your models here.

class CustomerInfo(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200, null=True)
    customer_organization = models.CharField(max_length=100, null=True)
    customer_email = models.CharField(max_length=200, null=True)
    customer_phone = models.CharField(max_length=11, unique=True, blank=True, null=True)
    profile_pic = models.ImageField(default='images/default-logo.png', null=True, blank=True)
    ctype = (
        ('IIG', 'IIG'),
        ('ISP', 'ISP'),
        ('NIX', 'NIX')
    )
    customer_type = models.CharField(max_length=100, null=True, choices=ctype)
    def __str__(self):
        return self.customer_name


class LocationInfo(models.Model):
    location_name = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.location_name

class DeviceInfo(models.Model):
    dtype = (
        ('Router', 'Router'),
        ('Switch', 'Switch'),
    )
    device_name = models.CharField(max_length=200, null=True)
    device_type = models.CharField(max_length=100, null=True, choices=dtype)
    device_location = models.ForeignKey(LocationInfo, on_delete=models.CASCADE)
    device_IP = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.device_name

class InterfaceInfo(models.Model):
    interface_name = models.CharField(max_length=200, null=True)
    interface_description = models.CharField(max_length=300, null=True)
    interface_graph = models.CharField(max_length=300, null=True, blank=True)
    device = models.ForeignKey(DeviceInfo, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        #return (self.device.device_name + ' - ' + self.interface_name)
        return (self.device.device_name + ' - ' + self.interface_description + ' - ' + self.interface_name)

class CustomerProperties(models.Model):
    unit = (
        ('Mbps', 'Mbps'),
        ('Gbps', 'Gbps'),
    )
    name = models.ForeignKey(CustomerInfo, null=True, on_delete=models.SET_NULL)
    connected_interface = models.ManyToManyField(InterfaceInfo)
    customer_location = models.ForeignKey(LocationInfo, on_delete=models.CASCADE)
    ASN = models.CharField(max_length=100, null=True, blank=True)
    peering_IP = models.CharField(max_length=100, null=True)
    peering_description = models.CharField(max_length=100, null=True, blank=True)
    #connected_device = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE)
    customer_Bandwidth = models.DecimalField(max_digits=10, decimal_places=2)
    customer_unit = models.CharField(max_length=20, null=True, choices=unit)
    
    def __str__(self):
        if self.peering_description:
            pd = self.peering_description
        else:
            pd = ''
        return (self.name.customer_name + ' ' + pd)
        #return (pd)

class EmailalertDB(models.Model):
    emailDB = models.EmailField(max_length=70, unique=True)
    users = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return (self.users.username + ' - ' + self.emailDB)

class PhonealertDB(models.Model):
    phoneDB = models.CharField(max_length=11, unique=True)
    users = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return (self.users.username + ' - ' + self.phoneDB)