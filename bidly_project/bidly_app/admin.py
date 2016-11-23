from django.contrib import admin

# Register your models here.
from .models import Auction, Bidly_User, Role, Item, Bid

admin.site.register(Auction)
admin.site.register(Bidly_User)
admin.site.register(Role)
admin.site.register(Item)
admin.site.register(Bid)