#-*- coding: utf-8 -*-
from django.contrib import admin
from autoanswer.models import RecCall, ReadCall
from django.conf.urls.defaults import *
from django.http import HttpResponse

class RecCallAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return self.model.objects.filter(read_at=None)

    def get_urls(self):
        urls = super(RecCallAdmin, self).get_urls()
        my_urls = patterns('',(r'(?P<aaid>\d+)/rm/$', self.admin_site.admin_view(self.rmaa)))
        return my_urls + urls

    def rmaa(self, request, aaid):
        u = request.user
        try:
            aa = RecCall.objects.get(id=int(aaid))
            aa.read(u)
            return HttpResponse("success", mimetype="text/plain")
        except:
            return HttpResponse("error", mimetype="text/plain")

    def get_actions(self, request):
        actions = super(RecCallAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def linkplay(self):
        return(u"<a href='#' onClick=\"set('/sounds/aa/%s', '%s - Звонок от %s, время: %s'); return false;\">Сообщение от абонента %s</a>" % (self.path, self.id, self.src, self.added_at.strftime('%H:%M:%s %Y.%m.%d'), self.src))
    linkplay.allow_tags = True
    linkplay.short_description = u'Источник'
    def linkdel(self):
        return(u"<a href='#' onClick=\"aadel(%s, $(this)); return false;\"><img src='/media/img/del.png' alt='Удалить' /></a>" % self.id)
    linkdel.allow_tags = True
    linkdel.short_description = u'Действия'
    list_display = (linkplay, linkdel,'added_at')

class ReadCallAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return self.model.objects.exclude(read_at=None)

    def linkplay(self):
        return(u"<a href='#' onClick=\"set('/sounds/aa/%s', '%s - Звонок от %s, время: %s'); return false;\">Сообщение от абонента %s</a>" % (self.path, self.id, self.src, self.added_at.strftime('%H:%M:%s %Y.%m.%d'), self.src))
    linkplay.allow_tags = True
    linkplay.short_description = u'Источник'

    def linkdel(self):
        return(u"<a href='%s/delete/'><img src='/media/img/del.png' alt='Удалить' /></a>" % self.id)
    linkdel.allow_tags = True
    linkdel.short_description = u'Действия'
    list_display = (linkplay, linkdel, 'manager', 'read_at', 'added_at')
    list_filter = ('manager',)

admin.site.register(RecCall, RecCallAdmin)
admin.site.register(ReadCall, ReadCallAdmin)
