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