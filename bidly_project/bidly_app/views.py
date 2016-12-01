from bidly_app.forms import UserForm, BidlyUserForm
from .models import Auction, Bidly_User, Role, Item, Bid
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext, Template
from django.template.context_processors import csrf
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import os
import json


# Create your views here.

@login_required(login_url='/user_login/')
def home(request):
	print("home: get_user(request)", get_user(request))
	print("home: request.user", request.user)
	context = {'user': get_user(request)}
	return render(request, 'home.html', context)

def profile(request):
	print("profile: get_user(request)", get_user(request))
	print("profile: request.user", request.user)
	return render(request, 'profile.html')

# add code to actually render page based on item requested
def item(request):
	itemId = request.GET.get('item_id')
	item = Item.objects.get(pk=itemId)
	name = item.name
	startingPrice = item.starting_price
	increment = item.increment
	imagePath = item.image_path
	value = item.value
	description = item.description

	context = {'name' : name, 'starting_price' : startingPrice, 'increment' : increment, 'image_path' : imagePath, 'value' : value, 'description' : description}
	return render(request, 'item_page.html', context)

def make_bid(request):
	itemId = request.POST.get('item_id')
	userId = request.POST.get('user_id')
	bidAmount = int(request.POST.get('bid'))

	print(request.user)
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
		print("login_1: get_user(request)", get_user(request))
		print("login_1: request.user", request.user)
		if user:
			if user.is_active:
				login(request, user)
				print("login_2: get_user(request)", get_user(request))
				print("login_2: request.user", request.user)
				return render_to_response('home.html', c, RequestContext(request))
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


# Need a way to have user id here too so can confirm old password entered is same as in database. And to update the password in the database I suppose...
def changepw(request):
	if request.method == 'POST':
		old_password = request.POST['oldpw']
		password = request.POST['newpw']
		password_confirm = request.POST['confirmpw']
		userId = 1 # HALPPPPP
		if password == password_confirm:
			user = Bidly_User.objects.get(pk=userId)
			user.set_password(password)
			user.save()
			return render_to_response('profile.html')
		else:
			return HttpResponse(json.dumps({'status' : 500, 'error' : "New Passwords Don't Match"}), content_type='application/json')

def change_profile(request):
	userId = request.POST['userId']
	username = request.POST['username']
	email = request.POST['email']
	phone_number = request.POST['phone_number']
	changed = False

	user = Bidly_User.objects.get(pk=userId)

	if user.get_username != username:
		user.set_username(username)
		changed = True
	if user.phone_number != phone_number:
		user.phone_number = phone_number
		changed = True
	if user.get_email != email:
		user.set_email(email)
		changed = True
	if changed:
		user.save()
		return render_to_response('profile.html')
	return HttpResponse(json.dumps({'status' : 500, 'error' : "Nothing Changed"}, content_type='application/json'))

def get_profile_info(request):
	# userId = request.GET.get('userId')
	# user = Bidly_User.objects.get(pk=userId)
	password = request.user.password
	bidly_user = Bidly_User.objects.get(user=request.user)
	phone_number = bidly_user.phone_number
	username = request.user.username
	email = request.user.email
	response = {'status': 200, 'username': username, 'email': email, 'phone_number': phone_number, 'password': password}
	return HttpResponse(json.dumps(response), content_type='application/json')