from django.contrib import admin

from .models import Category, Channel, Server

# Register your models here.
admin.site.register(Category)
admin.site.register(Channel)
admin.site.register(Server)
