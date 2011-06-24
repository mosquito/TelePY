#-*- coding: utf-8 -*-
from django.db.models import *
from datetime import datetime, date
from django.contrib.auth.models import User

class RecCall(Model):
    path = TextField(verbose_name=u'Путь')
    src = CharField(max_length=20, null=True, blank=True, verbose_name=u'Номер абонента')
    added_at = DateTimeField(auto_now_add=True, auto_now=False, verbose_name=u'Дата добавления')
    read_at = DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True, verbose_name=u'Дата удаления')
    manager = ForeignKey(User, null=True, blank=True, verbose_name=u'Менеджер')

    def read(self, user):
        self.read_at = datetime.now()
        self.manager = user
        self.save()

    def __unicode__(self):
        return u'Звонок от %s, время: %s' % (self.src, self.added_at)

    class Meta:
        ordering = ['-added_at',]
        unique_together = ('path',)
        verbose_name = u'Новая запись'
#        verbose_name_plural = u'Записи автоответчика(%s)' % RecCall.objects.filter(read_at=None).count()
        verbose_name_plural = u'Новые записи'

class ReadCall(RecCall):
    class Meta:
        proxy = True
        ordering = ['-read_at',]
        verbose_name = u'Прослушанная запись'
        verbose_name_plural = u'Прослушанные записи'
