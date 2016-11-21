from django.contrib import admin

# Register your models here.
from .models import Auction, User, Role, Item, Bid

admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Item)
admin.site.register(Bid)