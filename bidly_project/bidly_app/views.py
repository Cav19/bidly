from bidly_app.forms import UserForm, BidlyUserForm
from .models import Auction, Bidly_User, Role, Item, Bid, Category
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext, Template
from django.template.context_processors import csrf
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.auth.models import Group
from django.conf import settings as djangoSettings
from PIL import Image
from resizeimage import resizeimage
import base64
import os
import json
import operator
import re
import datetime
import random


# Create your views here.

def home(request, auction_name):
	"""
	Render the home page for the app.
	Param: auction_name refers to the name of the auction.
	All items for an auction are rendered on the home page.
	"""
	# Get the proper formating based on whether website is mobile or web
	css_path="CSS/home_admin.css"
	mode = is_request_mobile(request)
	if mode == "mobile":
		css_path = "CSS/home.css"

	# Get the auction and its items
	auction = Auction.objects.filter(url=auction_name)
	all_items = Item.objects.filter(auction=auction)

	# Sort items by category for category-based carousel display
	categories = []
	for item in all_items:
		if item.category not in categories:
			categories.append(item.category)
	items_by_category = {}
	for category in categories:
		items = all_items.filter(category=category)
		for item in items:
			item.description = item.description[:80] + "..."
		items_by_category[category] = items

	# Get popular items to populate the popular item carousel
	popular_items = get_popular_items(auction)

	# Render home page
	context = {
		'user': get_user(request), 
		'all_items' : all_items, 
		'popular_items' : popular_items, 
		'items_by_category' : items_by_category,
		'css_path': css_path,
	}
	return render(request, 'home.html', context)


def profile(request):
	"""
	Renders the profile page.
	"""

	# Get the proper formating based on whether website is mobile or web
	css_path="CSS/profile.css"
	mode = is_request_mobile(request)
	if mode == "mobile":
		css_path = "CSS/profile.css"
	
	# Find auctions user is an admin of
	user = request.user
	bidly_user = Bidly_User.objects.get(user=user)
	adminRoles = Role.objects.filter(user=bidly_user)
	adminAuctions = []
	for role in adminRoles:
		adminAuctions.append(role.auction)
	if mode == 'desktop':
		css_path = "CSS/profile_admin.css"

	# Get the winning and losing bids to populate the 'mybids' tab
	bids = get_win_loss_bids(request)
	winning_bids = bids[0]
	losing_bids = bids[1]
	context = {
		'winning_bids' : winning_bids, 
		'losing_bids' : losing_bids,
		'css_path': css_path,
		'mode': mode,
		'admin_auctions' : adminAuctions,
	}
	context.update(csrf(request))
	return render(request, 'profile.html', context)


#TODO: add code to actually render page based on item requested
def item(request):
	"""
	Renders an item page, with specific details for one item in an auction.
	"""
	# Get information associated with item.
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

	# Find if auction is active
	auction = item.auction
	auction_started = True
	if not auction.start_time or auction.end_time < datetime.datetime.now():
		auction_started = False

	# Get the proper formating based on whether website is mobile or web
	mode = is_request_mobile(request)
	cssFile = ""
	if mode == "desktop":
		cssFile = "CSS\item_page_desktop.css"
	elif mode == "mobile":
		cssFile = "CSS\item_page.css"

	# Render item page
	context = {
		'name' : name, 
		'starting_price' : startingPrice, 
		'increment' : increment, 
		'image_path' : imagePath, 
		'value' : value, 
		'description' : description, 
		'role' : groupName, 
		'mode' : mode, 
		'css_file' : cssFile,
		'auction_started': auction_started,
	}
	return render(request, 'item_page.html', context)


def make_bid(request):
	"""
	Allows users to place a bid. 
	"""
	# Get bid information
	itemId = request.POST.get('item_id')
	userId = request.POST.get('user_id')
	bidAmount = int(request.POST.get('bid'))

	item = Item.objects.get(pk=itemId)
	user = request.user
	bidly_user = Bidly_User.objects.get(user=user)

	#Check to make sure another higher bid hasn't come in. See if we can lock the database later to prevent race conditions
	bids = Bid.objects.filter(item_id=itemId).order_by('-timestamp')[:1]
	if len(bids) > 0:
		topBid = bids[0].amount
		if bidAmount <= topBid:
			return HttpResponse(json.dumps({'status' : 500, 'error' : "Bid too low"}), content_type='application/json')

	# Create the bid item
	newBid = Bid(item=item, user=bidly_user, amount=bidAmount)
	newBid.save()

	response = {'status' : 200, 'current_bid' : bidAmount}
	return HttpResponse(json.dumps(response), content_type='application/json')

def get_top_bid(request):
	"""
	Helper function to get the highest bid for an item.
	"""
	bids = Bid.objects.filter(item_id=request.GET.get('item_id')).order_by('-timestamp')[:1]
	if len(bids) > 0:
		topBid = bids[0].amount
	else :
		topBid = 0
	response = {'status' : 200, 'current_bid' : topBid, 'item_id' : request.GET.get('item_id')}
	return HttpResponse(json.dumps(response), content_type='application/json')

def search(request):
	"""
	Search functionality for home page
	Looks for an item with a matching name or id to the search input, 
	and redirects to that item page if it finds it.
	"""
	search_term = request.GET.get('search_term')
	auction = Auction.objects.filter(url=request.GET.get('auction_name'))
	all_items = Item.objects.filter(auction=auction)
	for item in all_items:
		if (item.name == search_term) or (str(item.id) == search_term):
			item_page = '/item_page/?item_id=' + str(item.id)
			response = {
				'status': 200, 
				'item_id': item.id, 
				'item_page': item_page,
				}
			return HttpResponse(json.dumps(response), content_type='application/json')
	return HttpResponse({'status': 204}, content_type='application/json')


def register(request):
	"""
	Pieces of register and user login code taken from 
	http://www.tangowithdjango.com/book/chapters/login.html

	The registration page allows users to create an account on the site.
	Accounts have a Django's user model and an additional Bidly profile model.
	When the user registers, their account is created, 
	they are logged in, and redirected to the home page.
	"""
	# Context: Format page based on user's browser (mobile or web)
	css_path = "CSS/login_web.css"
	mode = is_request_mobile(request)
	if mode == "mobile":
		css_path = "CSS/login.css"
	c = {'css_path': css_path, 'mode': mode}
	c.update(csrf(request))
	print(css_path)

	# Form models created in forms.py for collecting user registration data.
	user_form = UserForm()
	profile_form = BidlyUserForm()

	# Logic for registering an account
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = BidlyUserForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			# Create user object and password
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			# Create corresponding profile for the user
			profile = profile_form.save(commit=False)
			profile.user = user
			profile.save()

			# Assign user auction and default role as bidder
			group = Group.objects.get(name="bidder")
			auction = Auction.objects.get(pk=1) #TODO: change auction to be dynamic
			role = Role(auction=auction, role=group, user=profile)
			role.save()

			# Log in the newlyr registered user.
			login(request, user)

			# Redirect to the home page
			return home(request)
		else:
			# TODO: print error with user form validity
			print(user_form.errors, profile_form.errors)
			
	c['user_form'] = user_form
	c['profile_form'] = profile_form
	return render_to_response('login.html', c, RequestContext(request))


def user_login(request, auction_name=''):
	"""
	Pieces of register and user login code taken from 
	http://www.tangowithdjango.com/book/chapters/login.html

	The login page allows users to log in to an already created account.
	When the user logs in, they are redirected to the home page.
	"""
	# Context: Format page based on user's browser (mobile or web)
	css_path="CSS/login_web.css"
	mode = is_request_mobile(request)
	if mode == "mobile":
		css_path = "CSS/login.css"
	c = {'css_path': css_path, 'mode': mode, 'auction' : auction_name}
	c.update(csrf(request))

	# Log user in to account
	if request.method == 'POST':
		# Check that username and password match records
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				# Log user in, and redirect to home page
				login(request, user)
				print("login_2: get_user(request)", get_user(request))
				print("login_2: request.user", request.user)
				if auction_name != "":
					return HttpResponseRedirect('/home/' + auction_name + '/')
				else:
					return HttpResponseRedirect('/profile/')
			else:
				return HttpResponse("Your account is disabled.") #TODO: handle response
		else:
			print("Your username or password is incorrect")
			return HttpResponse("Invalid login details supplied") #TODO: handle  response
	else:
		return render_to_response('login.html', c, RequestContext(request))


def changepw(request):
	"""
	Allows users to change their password.
	Users must enter their old password, 
	and enter matching new passwords twice in order to change the password.
	NOT CURRENTLY FUNCTIONING (known csrf error)
	"""
	c = {}
	c.update(csrf(request))

	if request.method == 'POST':
		old_password = request.POST['oldpw']
		password = request.POST['newpw']
		password_confirm = request.POST['confirmpw']
		user = request.user

		# Check that user's password is correct
		if user.check_password(old_password):
			# Check that the new passwords match, and set the new password
			if password == password_confirm:
				user.set_password(password)
				user.save()
				# return HttpResponseRedirect('/user_login/')
				# return render_to_response('profile.html', c, RequestContext(request))
				return profile(request)
			else:
				return HttpResponse(json.dumps({'status' : 500, 'error' : "New Passwords Don't Match"}), content_type='application/json')
		else:
			return HttpResponse(json.dumps({'status': 500, 'error': "Your password was incorrect"}), content_type='application/json')


def change_profile(request):
	"""
	Updates user profile information if they alter it in their profile
	"""
	# Get user information
	userId = request.POST['userId']
	username = request.POST['username']
	email = request.POST['email']
	phone_number = request.POST['phone_number']
	changed = False
	user = Bidly_User.objects.get(pk=userId)

	# Check for changes, and update information if changes are found.
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
	"""
	Returns the profile information of the user who made the request.
	"""
	# userId = request.GET.get('userId')
	# user = Bidly_User.objects.get(pk=userId)
	password = request.user.password
	bidly_user = Bidly_User.objects.get(user=request.user)
	phone_number = bidly_user.phone_number
	username = request.user.username
	email = request.user.email
	response = {'status': 200, 'username': username, 'email': email, 'phone_number': phone_number, 'password': password}
	return HttpResponse(json.dumps(response), content_type='application/json')


def get_popular_items(auction):
	"""
	Retrieves the most popular items in an auction, based on the number of bids an item has
	"""
	item_counts = {}
	popular_items_tuples = []
	popular_bids = Bid.objects.filter(item__auction=auction) 

	# Count the number of bids per item
	for bid in popular_bids:
		if bid.item_id not in item_counts:
			item_counts[bid.item_id] = 1
		else:
			item_counts[bid.item_id] += 1
	for item in item_counts:
		popular_items_tuples.append((Item.objects.get(pk=item), item_counts[item]))
	popular_items = []

	# Find and return the most popular items
	for item in sorted(popular_items_tuples, key=lambda x: x[1], reverse=True):
		item[0].description = item[0].description[:80] + "..."
		popular_items.append(item[0])
	return popular_items


def get_win_loss_bids(request):
	"""
	Retrieves bids for a user, and classifies whether the user is winning the item or not.
	Returns a list of winning bids and a list of losing bids.
	"""
	# Get all of the bids
	all_items = Item.objects.all()
	user = Bidly_User.objects.get(user=request.user)
	all_bids = Bid.objects.filter(user=user).order_by('-timestamp') #Change this auction id later..order_by('-timestamp') #Change this auction id later.
	
	# Find whether a bid is winning or losing
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
				item.description = item.description[:80] + "..."
				if all_bids[0].user == user:
					winning_bids.append(item)
					break
				else:
					losing_bids.append(item)
					break
	return [winning_bids, losing_bids]

def is_request_mobile(request):
	"""
	Source: Matt Sullivan http://sullerton.com/2011/03/django-mobile-browser-detection-middleware/

	Checks whether a request was made by a mobile device or desktop device
	Returns a string with prediction of device type
	"""
	reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I|re.M)
	reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)
	if request.META['HTTP_USER_AGENT']:
		user_agent = request.META['HTTP_USER_AGENT']
		b = reg_b.search(user_agent)
		v = reg_v.search(user_agent[0:4])
		if b or v:
			return "mobile"

	return "desktop"

def create_auction(request):
	"""
	Creates an auction, using user inputed data, an uploaded spreadsheet for item information,
	and uploaded images.
	"""
	# Create new auction
	if request.method == "POST":
		url = request.POST.get("url")
		url = validate_url(url)
		newAuction = Auction(url=url)
		newAuction.save()
		
		#Create folder to store item images
		newDirectory = djangoSettings.STATIC_ROOT+"img/auction"+str(newAuction.pk)+"/"
		if not os.path.exists(newDirectory): #this could cause race condition, but shouldn't because all directory names are distinct, and only created when an auction is created
			os.mkdir(newDirectory)
		else:
			print("Error: " + newDirectory + " is already a directory.") #TODO: Handle error
		items = json.loads(request.POST.get('items'))  # I hate this as much as you do
		create_items_for_auction(items, newAuction, newDirectory)

		# Sets user creating the auction as the auction admin
		user = request.user
		bidly_user = Bidly_User.objects.get(user=user)
		adminGroup = Group.objects.get(name="admin")
		role = Role(user=bidly_user, auction=newAuction, role=adminGroup)
		role.save()

		response = {"status" : 200, "auction_id" : newAuction.pk, "auction_url" : newAuction.url}
		return HttpResponse(json.dumps(response), content_type='application/json')

def validate_url(url):
	"""
	When user creates an auction with a new url, check to make sure the url isn't already being used.
	URLs that are being used get a random 4-digit number appended to the end, to make them unique.
	"""
	# Preprocess url
	url = url.replace(" ", "_")
	auctionsWithUrl = Auction.objects.filter(url=url)
	newUrl = url
	# If the url is taken, append new 4 digit strings to the end until we reach a unique url
	while auctionsWithUrl.count() > 0:
		newUrl = url
		for i in range(4):
			randomDigit = random.randint(0,9)
			newUrl += str(randomDigit)
		
		auctionsWithUrl = Auction.objects.filter(url=newUrl)

	return newUrl
		
def create_items_for_auction(items, auction, imgDirectory):
	"""
	After an auction is created, this method creates item objects for each item in the auction.
	"""
	for item in items:
		# Get item information
		startingPrice = item["starting_price"]
		increment = item["increment"]
		name = item["name"]
		categoryName = item["category"]
		category = get_category_by_name(categoryName)
		value = item["value"]
		description = item["description"]

		# Create item
		itemObj = Item(auction=auction, starting_price=startingPrice, increment=increment, name=name, category=category, value=value, description=description)#leaves image_path null
		itemObj.save()

		itemId = itemObj.pk
		imageUrl = item["image_url"]
		convertedImg = convert_b64_to_img(imageUrl)

		
		#Find the image type
		imageType = imageUrl.split(";")[0]
		imageType = imageType.split("/")[1]

		#Save image in static directory
		imgPath = imgDirectory+str(itemId)+"."+imageType
		print("imgPath: " + imgPath)
		file = open(imgPath,"wb+")
		file.write(convertedImg)
		file.close()
		relativePath = imgPath.split("static/")[1]#assumes static/ occurs once in path
		itemObj.image_path = relativePath
		itemObj.save()
		# Resize uploaded images to be square (for prettiness)
		resize_images(itemObj)


def get_category_by_name(categoryName):
	"""
	Given the name of a category, it returns the category object.
	"""
	categoryName = categoryName.lower()
	categories = Category.objects.filter(category_name=categoryName)
	if len(categories) == 0:
		category = Category(category_name=categoryName)
		category.save()
	else:
		category = categories[0]

	return category

def convert_b64_to_img(imageUrl):
	"""
	Converts an image string in b64 to an image
	"""
	imgParts = imageUrl.split(",")
	imgdata = base64.b64decode(imgParts[1])
	return imgdata

def begin_auction(request):
	"""
	Starts the auction, allowing users to begin to place bids.
	"""
	auctionURL = request.POST.get("auction_url")
	auction = Auction.objects.get(url=auctionURL)
	
	# Update auction end time
	endTimeString = request.POST.get("end_time")
	dateTimeParts = endTimeString.split(" ")
	dateString = dateTimeParts[0]
	timeString = dateTimeParts[1]

	dateParts = dateString.split("-")
	year = int(dateParts[0])
	month = int(dateParts[1])
	day = int(dateParts[2])

	timeParts = timeString.split(":")
	hour = int(timeParts[0])
	minute = int(timeParts[1])

	endTime = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)

	# Ensure end time is in the future.
	if endTime < datetime.datetime.now():
		response = {"status":400, "error_message":"start_time is after end_time"}
		return HttpResponse(json.dumps(response), content_type='application/json')

	# Update start time and end time, so that auction is active
	auction.start_time = datetime.datetime.now()
	auction.end_time = endTime
	response = {"status":200, "auction_id":auction.pk, "auction_url":auctionURL}
	return HttpResponse(json.dumps(response), content_type='application/json')

def image_test(request):
	if request.method == "GET":
		auction = Auction.objects.get(pk=2)
		auction.delete()
		items = Item.objects.all()
		for item in items:
			print(str(item.pk)+"\t"+item.name + "\t" + str(item.auction.pk) +"\t" + str(item.category))
		return render(request,"image_test.html")
	else:
		name = "AI Project"
		auction = Auction.objects.get(pk=1)
		startingPrice = 400
		increment = 20
		category = Category.objects.get(pk=1)
		value = 600
		description = "Mediocre AI capstone project..."

		imageUrl = request.POST.get("image_url")
		imgParts = imageUrl.split(",")
		print(imgParts[0])
		imgdata = base64.b64decode(imgParts[1])
		file=open(djangoSettings.STATIC_ROOT+'img/test.png','wb+')
		file.write(imgdata)
		file.close()
		return HttpResponse(json.dumps({"status" : 200}), content_type='application/json')


def resize_images(item):
	"""
	After images are uploaded, they are all resized to be squares.
	This ensures each image fits into our template.
	"""
	# for item in items:
	img_path = djangoSettings.STATIC_ROOT + item.image_path
	image = Image.open(img_path)
	if image.mode not in ('L', 'RGB'):
		image = image.convert('RGB')
	size = min(image.width, image.height)
	image = resizeimage.resize_crop(image, [size,size])
	image.save(img_path, image.format)
