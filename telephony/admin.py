#-*- coding: utf-8 -*-

import operator
from re import compile
from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str
from django.conf.urls.defaults import *
from telepy.address.widgets import ForeignKeySearchInput

import string
from random import choice
from django.contrib import admin
from telephony.models import *
from datetime import datetime, timedelta
from django import forms
from django.db import models

class CdrAdmin(admin.ModelAdmin):
    def billsec_norm(obj):
        return timedelta(seconds=obj.billsec)
    billsec_norm.short_description = u'Учтено мин.'

    def linksrc(self):
        return u"""<a style='font-size: 12px' href='/admin/telephony/numbers/?accountcode=%s'><b>%s</b></a> <a href='?src=%s'><img style='float: right' src='/media/img/filter.png'></a>""" % (self.accountcode_id,self.src, self.src)
    linksrc.allow_tags = True
    linksrc.short_description = u'Номер исходящего |  Фильтр'

    def linkdst(self):
        return u"""%s<a href='?dst=%s'><img style='float: right' src='/media/img/filter.png'></a>""" % (self.dst, self.dst)
    linkdst.allow_tags = True
    linkdst.short_description = u'Номер исходящего |  Фильтр'

    def linkplay(self):
        if self.callrecord:
            return(u"<a href='#' onClick=\"set('/sounds/rec/%s', 'Звонок от %s, на: %s', $(this)); return false;\"><img src='/media/img/play.png' alt='Проиграть' /></a>" % (self.callrecord.name, self.src, self.dst))
        else:
            return(u"&nbsp;")
    linkplay.allow_tags = True
    linkplay.short_description = u' '

    list_display = ('start', linkplay, linksrc, linkdst, 'dcontext', billsec_norm, 'disposition',)
    list_filter = ('dcontext', 'disposition', 'amaflags', 'start',)
    search_fields = ('src','dst',)

    ordering = ['-start',]

    def get_actions(self, request):
        actions = super(CdrAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

class VoicemailAdmin(admin.ModelAdmin):
    list_display = ('payer', 'mailbox', 'password', 'stamp')
    search_fields = ('mailbox__name',)
    ordering = ['mailbox__name',]
    list_display_links = ('mailbox',)

    def save_model(self, request, obj, form, change, *args, **kwargs):
        if isinstance(obj.password, type(None)): obj.password=''
        if len(obj.password)==0:
            obj.gen_passwd()
        obj.payer=obj.mailbox.accountcode
        obj.save()

class NumbersAdmin(admin.ModelAdmin):
    list_display = ('name', 'secret', 'callerid', 'context', 'host', 'ipaddr')
    list_filter = ('commented', 'context', 'amaflags', 'dtmfmode')
    search_fields = ('name',)
    ordering = ['name',]
    radio_fields = {"dtmfmode": admin.VERTICAL, "insecure": admin.VERTICAL, "type": admin.VERTICAL, "amaflags": admin.VERTICAL,  }

    def get_readonly_fields(self, request, obj=None):
        fields = super(NumbersAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return ('host','nat','type','amaflags','callgroup','callerid',
                    'cancallforward','directmedia','defaultip','dtmfmode', 'port',
                    'insecure','language','mailbox','musiconhold','pickupgroup', 'directmedia',
                    'qualify','disallow','allow','trustrpid','sendrpid','videosupport')
        return fields

    def get_actions(self, request):
        actions = super(NumbersAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

class ExtensionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'commented', 'context', 'exten', 'priority', 'app', 'appdata', )
    ordering = ['context__name', 'exten', 'priority',]
    search_fields = ('=app','appdata')
    list_filter = ('context', 'exten')
    list_editable = ('commented', 'context', 'exten', 'priority', 'app', 'appdata', )
    list_display_links = ('id',)

admin.site.register(Cdr, CdrAdmin)
admin.site.register(Contexts)
admin.site.register(Numbers, NumbersAdmin)
admin.site.register(Extensions, ExtensionsAdmin)
admin.site.register(Voicemail, VoicemailAdmin)
admin.site.register(Queue)
admin.site.register(QueueMember)
