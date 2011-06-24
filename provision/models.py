#-*- coding: utf-8 -*-
from django.db.models import *
from os import path
from re import compile
from ConfigParser import ConfigParser
from django.db import connection, transaction
from random import randint as random

class Types(Model):
    name = CharField(max_length=50, default='Unknown Device', blank=False, primary_key=True, verbose_name='название', db_index=True)
    alias = CharField(max_length=50, blank=False, verbose_name=u'алиас', db_index=True)
    template = CharField(max_length=50, blank=False, verbose_name=u'темплейт', db_index=True)

    def __unicode__ (self, *args, **kwargs):
        return unicode("%s" % (self.name))
    class Meta:
        ordering = ['name']
        verbose_name = 'тип'
        verbose_name_plural = 'типы'
    def save(self, *args, **kwargs):
        if not path.exists('%s/%s' % (path.dirname(__file__)+'/scheme', self.name)):
            raise Exception('FileNotFound', 'File \"%s\" not found' % ('%s/%s' % (path.dirname(__file__)+'/scheme', self.name)))
        super(Types,self).save()

class DefaultConfig(Model):
    id = AutoField(primary_key=True, verbose_name=u'идентификатор')
    dtype = ForeignKey(Types, verbose_name=u'тип устройства')
    section = CharField(max_length=100, blank=False, default=u'flat-profile', verbose_name=u'секция', db_index=True)
    param = CharField(max_length=100, blank=False, verbose_name=u'параметр', db_index=True)
    value = CharField(max_length=100, null=True, blank=True, verbose_name=u'значение', db_index=True)
    class Meta:
        unique_together = (('dtype', 'section', 'param'),)
        ordering = ['dtype',]
        verbose_name = u'параметр по умолчанию'
        verbose_name_plural = u'конфигурация по умолчанию'
    def __unicode__ (self, *args, **kwargs):
        return unicode(u"(%s) %s | %s==%s" % (self.dtype, self.section, self.param, self.value))

class Configs(Model):
    id = AutoField(primary_key=True, verbose_name=u'идентификатор')
    device = ForeignKey('Devices', verbose_name=u'устройство')
    section = CharField(max_length=100, blank=False, default=u'flat-profile', verbose_name=u'секция', db_index=True)
    param = CharField(max_length=100, blank=False, verbose_name=u'параметр', db_index=True)
    value = CharField(max_length=100, null=True, blank=True, verbose_name=u'значение', db_index=True)

    class Meta:
        unique_together = (('device', 'section', 'param'),)
        ordering = ['device']
        verbose_name = u'конфигурация'
        verbose_name_plural = u'конфигурации'
    def __unicode__ (self, *args, **kwargs):
        return unicode(u"%s | %s==%s" % (self.section, self.param, self.value))

class Nets(Model):
    name = CharField(max_length=30, blank=False, null=False, verbose_name=u'название', db_index=True)
    start = IPAddressField(blank=False, null=False, verbose_name=u'начальный адрес', db_index=True)
    net   = PositiveSmallIntegerField(blank=False, null=False, verbose_name=u'подсеть', db_index=True)
    domain_name = CharField(max_length=30, blank=False, null=False, verbose_name=u'доменное имя', db_index=True)
    domain_name_servers = CharField(max_length=255, blank=False, null=False, verbose_name=u'DNS Серверы', db_index=True, help_text=u"DNS серверы через запятую")
    routers = IPAddressField(blank=False, null=False, verbose_name=u'шлюз по умолчанию', db_index=True)
    lease_time = PositiveIntegerField(blank=False, null=False, verbose_name=u'время аренды', db_index=True)
    max_lease_time = PositiveIntegerField(blank=False, null=False, verbose_name=u'максимальное время аренды', db_index=True)
    tftp = IPAddressField(blank=False, null=False, verbose_name=u'TFTP сервер', db_index=True)

    class Meta:
        unique_together = (('name',), ('start','net',))
        ordering = ['name',]
        verbose_name = u'подсеть'
        verbose_name_plural = u'подсети'

    def __unicode__(self, *args, **kwargs):
        return unicode(u'%s (%s/%s)' % (self.name, self.start, self.net))

class Devices(Model):
    STATES = (
        (0, u'Работает'),
        (1, u'Не работает'),
        (2, u'Потери'),
        (3, u'ХЗ'),
    )
    address = ForeignKey('address.Unit', verbose_name=u'адрес')
    enable = BooleanField(default=True, blank=False, verbose_name=u'работает')
    mac = CharField(max_length=17, default='00:00:00:00:00:00', blank=False, verbose_name=u'MAC-Адрес', db_index=True)
    ip = IPAddressField(blank=True, verbose_name=u'IP-Адрес', default='0.0.0.0', db_index=True)
    sn = CharField(max_length=50, default='000000000000', blank=False, verbose_name=u'серийный номер', db_index=True)
    type = ForeignKey('Types', verbose_name=u'тип')
    rra = FileField(upload_to="rra/", verbose_name=u'Round Robin Archive', blank=True, null=True, editable=False)
    state = PositiveSmallIntegerField(verbose_name=u'состояние', db_index=True, blank=True, null=True, default=3, choices=STATES, editable=False)
    subnet = ForeignKey('Nets', verbose_name=u'подсеть', db_index=True, null=False, blank=False)
    init_file = CharField(max_length=50, default=u'linksys.cfg', blank=False, verbose_name=u'файл начальной конфигурации', db_index=True)
    
    class Meta:
        unique_together = (('mac', 'sn'), ('ip',))
        ordering = ['enable', 'id', 'ip']
        verbose_name = u'устройство'
        verbose_name_plural = u'устройства'

    def __unicode__(self, *args, **kwargs):
        return unicode(u'%s (%s)' % (self.ip,self.id))

    def dict(self, *args, **kwargs):
        return dict(ip=self.ip, id=self.id, mac=self.mac, enable=self.enable, sn=self.sn, type=self.type)

class Ports(Model):
    port = PositiveIntegerField(default=None, editable=False, blank=False, null=False, verbose_name=u'порт')
    device = ForeignKey(Devices, verbose_name=u'устройство', editable=False, db_index=True)
    user = OneToOneField('telephony.Numbers', blank=True, null=True, verbose_name=u'номер')

    class Meta:
        unique_together = (('device', 'port'), ('user',))
        ordering = ('device', 'port',)
        verbose_name = u'порт'
        verbose_name_plural = u'порты'

    def __init__(self, *args, **kwargs):
        try:
            self.olduser=self.user
        except:
            self.olduser=None
        super(Ports, self).__init__(*args, **kwargs)

    def __unicode__(self, *args, **kwargs):
        if not isinstance(self.user, type(None)):
            return unicode(u'Порт: %s на устройстве: %s - %s (%s), привязян номер %s' % (self.port, self.device.type.name, self.device.address, self.device.ip, self.user.name))
        return unicode(u'Порт: %s на устройстве: %s - %s (%s)' % (self.port, self.device.type.name, self.device.address, self.device.ip))

