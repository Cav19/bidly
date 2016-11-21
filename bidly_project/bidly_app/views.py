from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Context, loader
import os


# Create your views here.

def login(request):
	return render(request, 'login.html')

	#cwd = os.getcwd()
	#print(cwd)
	#return render_to_response('Templates/login.html')