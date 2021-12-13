from django.contrib import admin

from hob.models import UserAccount, Hobby, FriendRequest

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Hobby)
admin.site.register(FriendRequest)