#-*- coding: utf-8 -*-

from django.contrib import admin
from models import *


from widgets import ForeignKeySearchInput
from django.conf.urls.defaults import *
from django.db import models
import operator
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str


class StreetAdmin(admin.ModelAdmin):
    list_display = ('town','name',)
    list_filter = ('town',)
    search_fields = ('street',)

class HouseAdmin(admin.ModelAdmin):
    list_display = ('street', 'num', 'sub',)
    list_filter = ('street',)
    search_fields = ('house','street__street',)

class OfficeAdmin(admin.ModelAdmin):
    list_display = ('house', 'name',)

class UnitAdmin(admin.ModelAdmin):
    list_display = ('office', 'name',)

admin.site.register(City)
admin.site.register(Street, StreetAdmin)
admin.site.register(House, HouseAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Unit, UnitAdmin)
