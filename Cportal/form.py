from django.db.models import fields
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class CreateUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1','password2', 'email', 'groups']

class CustomeraddInfo(ModelForm):
    class Meta:
        model = CustomerInfo
        fields = '__all__'

class CustomerprofileInfo(ModelForm):
    class Meta:
        model = CustomerInfo
        fields = '__all__'
        exclude = ['username']

class CustomeraddProperties(ModelForm):
    class Meta:
        model = CustomerProperties
        fields = '__all__'

class LocationaddInfo(ModelForm):
    class Meta:
        model = LocationInfo
        fields = '__all__'

class InterfaceaddInfo(ModelForm):
    class Meta:
        model = InterfaceInfo
        fields = '__all__'

class DeviceaddInfo(ModelForm):
    class Meta:
        model = DeviceInfo
        fields = '__all__'
    def clean_name(self):
        name = self.cleaned_data.get('device_name')
        name_match = DeviceInfo.objects.filter(device_name=name)
        if self.instance and self.instance.pk and not name_match:
            return name
        else:
            raise forms.ValidationError("already exists")
    
class EmailDBaddInfo(ModelForm):
    class Meta:
        model = EmailalertDB
        fields = '__all__'

class PhoneDBaddInfo(ModelForm):
    class Meta:
        model = PhonealertDB
        fields = '__all__'

class ContactForm(forms.Form):
	first_name = forms.CharField(max_length = 50)
	last_name = forms.CharField(max_length = 50)
	email_address = forms.EmailField(max_length = 150)
	message = forms.CharField(widget = forms.Textarea, max_length = 2000)
