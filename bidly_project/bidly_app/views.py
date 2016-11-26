from bidly_app.forms import UserForm, BidlyUserForm
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Context, loader
import os


# Create your views here.

def login(request):
	return render(request, 'login.html')

def home(request):
	return render(request, 'home.html')

def profile(request):
	return render(request, 'profile.html')

def register(request):
	context = RequestContext(request)
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = BidlyUserForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user
			profile.save()

			registered = True

		else:
			print user_form.errors, profile_form.errors

	else:
		user_form = UserForm()
		profile_form = BidlyUserForm()

	return render_to_response(
			'bidly_app/login.html',
			{'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, 
			context)
