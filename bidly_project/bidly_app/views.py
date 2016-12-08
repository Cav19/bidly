from bidly_app.forms import UserForm, BidlyUserForm
from .models import Auction, Bidly_User, Role, Item, Bid, Category
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext, Template
from django.template.context_processors import csrf
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.auth.models import Group
import os
import json
import operator
import re

# Create your views here.

#@login_required(login_url='/user_login/')
def home(request):
	css_path="CSS/home_admin.css"

	all_items = Item.objects.all()
	print(all_items)
	all_categories = Category.objects.all()
	items_by_category = {}
	for category in all_categories:
		items = Item.objects.filter(category=category)
		for item in sorted(items):
			item.description = item.description[:80] + "..."
		items_by_category[category] = items
	popular_items = get_popular_items()
	print("home: get_user(request)", get_user(request))
	print("home: request.user", request.user)
	context = {
		'user': get_user(request), 
		'all_items' : all_items, 
		'popular_items' : popular_items, 
		'items_by_category' : items_by_category,
		'css_path': css_path,
	}
	return render(request, 'home.html', context)

def profile(request):
	print("profile: get_user(request)", get_user(request))
	print("profile: request.user", request.user)
	bids = get_win_loss_bids(request)
	winning_bids = bids[0]
	losing_bids = bids[1]
	context = {'winning_bids' : winning_bids, 'losing_bids' : losing_bids}
	return render(request, 'profile.html', context)

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

	user = request.user
	bidly_user = Bidly_User.objects.get(user=user)
	role = Role.objects.get(user=bidly_user)
	groupName = role.role.name

	mode = is_request_mobile(request)
	cssFile = ""
	if mode == "desktop":
		cssFile = "CSS\item_page_desktop.css"
	elif mode == "mobile":
		cssFile = "CSS\item_page.css"

	context = {'name' : name, 'starting_price' : startingPrice, 'increment' : increment, 'image_path' : imagePath, 'value' : value, 'description' : description, 'role' : groupName, 'mode' : mode, 'css_file' : cssFile}
	return render(request, 'item_page.html', context)

def make_bid(request):
	itemId = request.POST.get('item_id')
	userId = request.POST.get('user_id')
	bidAmount = int(request.POST.get('bid'))

	item = Item.objects.get(pk=itemId)
	user = request.user
	bidly_user = Bidly_User.objects.get(user=user)
	#Check to make sure another higher bid hasn't come in. see if we can lock the database later to prevent race conditions
	bids = Bid.objects.filter(item_id=itemId).order_by('-timestamp')[:1]
	if len(bids) > 0:
		topBid = bids[0].amount
		if bidAmount <= topBid:
			return HttpResponse(json.dumps({'status' : 500, 'error' : "Bid too low"}), content_type='application/json')

	newBid = Bid(item=item, user=bidly_user, amount=bidAmount)
	newBid.save()

	response = {'status' : 200, 'current_bid' : bidAmount}
	return HttpResponse(json.dumps(response), content_type='application/json')

def get_top_bid(request):
	bids = Bid.objects.filter(item_id=request.GET.get('item_id')).order_by('-timestamp')[:1]
	if len(bids) > 0:
		topBid = bids[0].amount
	else :
		topBid = 0
	response = {'status' : 200, 'current_bid' : topBid, 'item_id' : request.GET.get('item_id')}
	return HttpResponse(json.dumps(response), content_type='application/json')

def register(request):
	css_path = "CSS/login_web.css"
	mobile = False
	if is_request_mobile(request) == "mobile":
		css_path = "CSS/login.css"
	c = {'css_path': css_path, 'mobile': mobile}
	c.update(csrf(request))

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

			#TODO: change auction to be dynamic, and establish how different account are 'promoted'
			group = Group.objects.get(name="bidder")
			auction = Auction.objects.get(pk=1)
			role = Role(auction=auction, role=group, user=profile)
			role.save()

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
	css_path="CSS/login_web.css"
	mobile = False
	if is_request_mobile(request) == "mobile":
		css_path = "CSS/login.css"
		mobile = True
	c = {'css_path': css_path, 'mobile': mobile}
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
				return home(request)
				# return render_to_response('home.html', c, RequestContext(request))
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

def get_popular_items():
	item_counts = {}
	popular_items_tuples = []
	popular_bids = Bid.objects.filter(item__auction_id=1) #Change this auction id later. 
	for bid in popular_bids:
		if bid.item_id not in item_counts:
			item_counts[bid.item_id] = 1
		else:
			item_counts[bid.item_id] += 1
	for item in item_counts:
		popular_items_tuples.append((Item.objects.get(pk=item), item_counts[item]))
	popular_items = []
	for item in sorted(popular_items_tuples, key=lambda x: x[1], reverse=True):
		item[0].description = item[0].description[:80] + "..."
		popular_items.append(item[0])
	return popular_items

def get_win_loss_bids(request):
	all_items = Item.objects.filter(auction_id=1)
	user = Bidly_User.objects.get(user=request.user)
	all_bids = Bid.objects.filter(item__auction_id=1, user=user).order_by('-timestamp') #Change this auction id later.
	winning_bids = []
	losing_bids = []
	for item in all_items:
		item_bids = Bid.objects.filter(item=item).order_by('-timestamp')
		if len(item_bids) > 0:
			top_bid = item_bids[0]
		else:
			continue
		for bid in all_bids:
			if bid.item == item:
				if all_bids[0].user == user:
					winning_bids.append(item)
					break
				else:
					losing_bids.append(item)
					break
	return [winning_bids, losing_bids]

def is_request_mobile(request):
	# Ported by Matt Sullivan http://sullerton.com/2011/03/django-mobile-browser-detection-middleware/
	reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I|re.M)
	reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)
	if request.META['HTTP_USER_AGENT']:
		user_agent = request.META['HTTP_USER_AGENT']
		b = reg_b.search(user_agent)
		v = reg_v.search(user_agent[0:4])
		if b or v:
			return "mobile"

	return "desktop"
