from bidly_app.forms import UserForm, BidlyUserForm
from .models import Auction, Bidly_User, Role, Item, Bid
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.template.context_processors import csrf
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
import os
import json


# Create your views here.

def login(request):
	return render(request, 'login.html')

def home(request):
	return render(request, 'home.html')

def profile(request):
	return render(request, 'profile.html')

# add code to actually render page based on item requested
def item(request):
	itemId = request.GET.get('item_id')
	print(itemId)
	return render(request, 'item_page.html')

def make_bid(request):
	itemId = request.POST.get('item_id')
	userId = request.POST.get('user_id')
	bidAmount = int(request.POST.get('bid'))

	item = Item.objects.get(pk=itemId)
	user = Bidly_User.objects.get(pk=userId)
	#Check to make sure another higher bid hasn't come in. see if we can lock the database later to prevent race conditions
	bids = Bid.objects.filter(item_id=itemId).order_by('-timestamp')[:1]
	topBid = bids[0].amount
	if bidAmount <= topBid:
		return HttpResponse(json.dumps({'status' : 500, 'error' : "Bid too low"}), content_type='application/json')

	newBid = Bid(item=item, user=user, amount=bidAmount)
	newBid.save()

	response = {'status' : 200, 'current_bid' : bidAmount}
	return HttpResponse(json.dumps(response), content_type='application/json')

def get_top_bid(request):
	bids = Bid.objects.filter(item_id=request.GET.get('item_id')).order_by('-timestamp')[:1]
	topBid = bids[0].amount
	response = {'status' : 200, 'current_bid' : topBid}
	return HttpResponse(json.dumps(response), content_type='application/json')

def register(request):
	registered = False
	c = {}
	c.update(csrf(request))

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
			return HttpResponseRedirect('/home/')
		else:
			print(user_form.errors, profile_form.errors)
			
	else:
		user_form = UserForm()
		profile_form = BidlyUserForm()

	c['user_form'] = user_form
	c['profile_form'] = profile_form
	c['registered'] = registered
	return render_to_response(
			'login.html', 
			c, 
			RequestContext(request))

def user_login(request):
	c = {}
	c.update(csrf(request))

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request)
				return HttpResponseRedirect('/home/')
			else:
				return HttpResponse("Your account is disabled.")
		else:
			print("Your username or password is incorrect")
			return HttpResponse("Invalid login details supplied")
	else:
		return render_to_response(
			'login.html', 
			c, 
			RequestContext(request))
