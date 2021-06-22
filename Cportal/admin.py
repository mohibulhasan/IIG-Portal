from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.
#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(DeviceInfo)
admin.site.register(InterfaceInfo)
admin.site.register(LocationInfo)
admin.site.register(CustomerInfo)
admin.site.register(CustomerProperties)
admin.site.register(EmailalertDB)
admin.site.register(PhonealertDB)
