#-*- coding: utf-8 -*-
from django.db.models import *

class City(Model):
    name = CharField(max_length=1000, blank=False, default=u'Брянск', verbose_name=u'город', db_index=True)
    class Meta:
        verbose_name = u'город'
        verbose_name_plural = u'города'

    def __unicode__(self,*args, **kwargs):
        return u'г. %s' % (self.name,)

class Street(Model):
    town = ForeignKey('City', verbose_name=u'город', db_index=True)
    name = CharField(max_length=255, blank=False, verbose_name=u'улица', db_index=True)

    class Meta:
        ordering = ['name',]
        unique_together = (('name',),)
        verbose_name = u'улица'
        verbose_name_plural = u'улицы'

    def __unicode__(self, *args, **kwargs):
        return u'г. %s ул. %s' % (self.town.name, self.name)

class House(Model):
    street = ForeignKey('Street', verbose_name=u'улица', db_index=True)
    num = CharField(max_length=100, blank=False, verbose_name=u'дом', db_index=True)
    sub = CharField(max_length=100, blank=True, default='0', verbose_name=u'корпус', db_index=True)

    class Meta:
        unique_together = (('street', 'num', 'sub',),)
        verbose_name = u'дом'
        verbose_name_plural = u'дома'

    def __unicode__(self,*args, **kwargs):
        if self.sub == None:
            return unicode(u"%s д.%s" % (self.street.__unicode__(), self.num,))
        elif len(self.sub):
            return unicode(u"%s д.%s/%s" % (self.street.__unicode__(), self.num, self.sub))
        else:
            return unicode(u"%s д.%s" % (self.street.__unicode__(), self.num,))

class Office(Model):
    house = ForeignKey('House', verbose_name=u'дом', db_index=True)
    name = CharField(max_length=100, blank=False, verbose_name=u'имя', db_index=True)

    class Meta:
        unique_together = (('house', 'name',),)
        verbose_name = u'офис'
        verbose_name_plural = u'офисы'

    def __unicode__(self,*args, **kwargs):
        return unicode(u"%s \"%s\"" % (self.house.__unicode__(), self.name,))

class Unit(Model):
    office = ForeignKey('Office', verbose_name=u'офис', db_index=True)
    name = CharField(max_length=100, blank=False, verbose_name=u'имя', db_index=True)

    class Meta:
        unique_together = (('office', 'name',),)
        verbose_name = u'подразделение'
        verbose_name_plural = u'подразделения'

    def __unicode__(self,*args, **kwargs):
        return unicode(u"%s %s" % (self.office.__unicode__(), self.name,))
