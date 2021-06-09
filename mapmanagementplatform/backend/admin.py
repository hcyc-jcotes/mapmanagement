"""
FOR MILESTONE 1 - TEAM 03

PROVIDES ADMIN RIGHTS TO THE MODELS STORED IN DB
"""
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Sequence)
admin.site.register(User)
admin.site.register(Region)
admin.site.register(Coordinate_property)