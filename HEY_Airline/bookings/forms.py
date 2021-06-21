from django import forms
from django.forms import modelformset_factory
from bookings.models import USER_INFO, PASSENGER
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username', 'password','email')

class UserProfileInfoForm(forms.ModelForm):
     class Meta():
         model = USER_INFO
         fields = ('phone','profile_pic')

passengerSet = modelformset_factory( PASSENGER, exclude=("PID", "airplane_number","user","trip_id"), extra = 1,can_delete=True)