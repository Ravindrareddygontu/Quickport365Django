from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ParcelDetails, OrderDetails, Complaint,Admin_driver
from django.core.exceptions import ValidationError
import requests


class SignUpForm(UserCreationForm):
    password2 = forms.CharField(label='Confirm Password (again)', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {'email': 'Email'}


class DomesticForm(forms.Form):
    origin_pincode = forms.IntegerField()
    destination_pincode = forms.IntegerField()

    def address_with_pincode(self, pincode):
        print('----------------')
        response = requests.get(f"https://api.postalpincode.in/pincode/{pincode}").json()
        print(response,'----------------')
        address = {}
        for i in response:
            address['city'] = i['PostOffice'][0]['Block']
            address['district'] = i['PostOffice'][0]['District']
            address['state'] = i['PostOffice'][0]['State']
        return address

    def clean(self):
        origin_pincode = self.cleaned_data.get('origin_pincode')
        destination_pincode = self.cleaned_data.get('destination_pincode')
        try:
            self.address_with_pincode(origin_pincode)
        except Exception as e:
            print(e, 'error')
            self.add_error('origin_pincode', 'Please enter a valid origin pincode')
        try:
            self.address_with_pincode(destination_pincode)
        except Exception as e:
            print(e, 'error')
            self.add_error('destination_pincode', 'Please enter valid destination Pincode')


class InternationalForm(forms.Form):
    destination_country = forms.CharField()
    origin = forms.IntegerField()
    destination = forms.IntegerField()
    labels = {'destination_country':'destination country', 'origin': 'origin pincode', 'destination': 'destination pincode'}


class ParcelDetailsForm(forms.ModelForm):
    item_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max should be 6kg'}))
    pickup_date = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}))

    class Meta:
        model = ParcelDetails
        fields = "__all__"

    def clean(self):
        item_weight = self.cleaned_data['item_weight']
        if item_weight > 6:
            return self.add_error('item_weight', 'Item should be below 6kgs')


class OrderDetailsForm(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = ['picked']


class UpdateOrderStatus(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = ['status']


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = '__all__'

proof_choices = (
    ("Aadhar", "Aadhar"),
    ("Driving_license", "Driving_license"),
    ("Voter_id", "Voter_id"),
    ("pancard", "pancard"),
)


class AdminDriverForm(forms.ModelForm):
    class Meta:
        model = Admin_driver
        fields = ['name', 'email', 'phone']


class DriverDetailsForm(forms.ModelForm):
    password2 = forms.CharField(label='Confirm Password (again)', widget=forms.PasswordInput)
    class Meta:
        model = Admin_driver
        exclude = ['flag']

    def save(self, commit=True):
        self.instance.flag = True
        return super().save(commit=commit)
