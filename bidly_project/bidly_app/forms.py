from bidly_app.models import Bidly_User
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

class BidlyUserForm(forms.ModelForm):
	class Meta:
		model = Bidly_User
		fields = ('phone_number')