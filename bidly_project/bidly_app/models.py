from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
# Create your models here.

class Auction(models.Model):
	start_time = models.DateTimeField('start_time')
	end_time = models.DateTimeField('end_time')
	url = models.CharField(max_length=50)

class Bidly_User(models.Model):
	user = models.OneToOneField(User)
	# user = models.ForeignKey(User, on_delete=models.CASCADE)
	phone_number = models.CharField(max_length=11)

	# def __str__(self):
	# 	return self.username

class Role(models.Model):
	auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
	user = models.ForeignKey(Bidly_User, on_delete=models.CASCADE)
	role = models.ForeignKey(Group, on_delete=models.CASCADE)

class Item(models.Model):
	auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
	starting_price = models.IntegerField(default=0)
	increment = models.IntegerField(default=1)
	name = models.CharField(max_length=30)
	image_path = models.CharField(max_length=100)
	# picture = models.ImageField(upload_to='item_images', blank=True)
	value = models.IntegerField(default=0)
	description = models.CharField(max_length=500)

	def __str__(self):
		return self.name

class Bid(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	user = models.ForeignKey(Bidly_User, on_delete=models.CASCADE)
	timestamp = models.DateTimeField('bid_time')
	amount = models.IntegerField(default=0)

