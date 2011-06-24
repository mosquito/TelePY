#-*- coding: utf-8 -*-

import operator
from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str
from django.conf.urls.defaults import *

from address.widgets import ForeignKeySearchInput
from django.contrib import admin
from provision.models import *
from telephony.models import Numbers
from django.forms.formsets import formset_factory
from django.forms import TextInput
from django import forms
from os import system
from re import compile
from sys import stdout
from ipaddr import IPv4

class TypesAdmin(admin.ModelAdmin):
    list_display = ('name','alias','template',)
    ordering = ('name',)
    search_fields = ('name','alias',)

    def save_model(self, request, obj, form, change):
        # Нужно создать DefaultConfig если его нет
        # создаю коусор
        cursor = connection.cursor()
        # выполняю запрос где считаю колличество конфигов по умолчанию
        cursor.execute('select count(*) FROM provision_types as t, provision_defaultconfig as c WHERE c.dtype_id = t.name and c.dtype_id = \'%s\' ;' % (obj.name,))
        if int(cursor.fetchone()[0]) > 0 :
            # если больше 0 то сохраняю объект, считая что дефолтконфиг для этого устройства уже создан
            cursor.close()
            # все
            return obj.save()
        else:
            # иначе просто закрываю курсор
            cursor.close()
            obj.save()

        try:
            # пробую открыть файл схемы
            filename = '%s/%s' % (path.dirname(__file__)+'/scheme', obj.name)
            scheme=open(filename, 'r')
        except:
            # если не открывается то вызываю ексепшн
            raise Exception('FileNotFound', 'File \"%s\" not found' % (filename))

        # читаю всю схему
        scheme=scheme.readlines()

        # инициализирую список регексов
        re=dict()
        # инициализирую словарь со схемой
        scheme_dict=dict()
        # регекс для секции
        re['section']=compile('\[(?P<section>[\w\s]+)\]\n')
        # регекс для параметров
        re['data']=compile('^(?P<param>[0-9\s\w\_\-\+\.\,]+)=(?P<value>.{0,})\n')

        # погнали по списку схемы
        for item in scheme:
            # если регекс секций возвращает что нибудь значит далее попрет секция
            if re['section'].findall(item):
                # выдергиваем название секции, в переменную которая выполняет роль буфера текущей секции
                section=re['section'].match(item).groupdict()['section']
                # добавляем ключ с именем секции в словарь и инициализируем как вложенный словарь
                scheme_dict[section]=dict()

            # если регекс даррых возвращает данные, то перед нами данные предидущей секции
            if re['data'].findall(item):
                # регексим в l строку, на выходе по идее словарь из dict(param=str(), value=str())
                l=re['data'].findall(item)[0]
                # суем в текущую секцию
                scheme_dict[section][l[0]]={ 'data': l[1], }

        # инициализирую словарь с инсертами
        insert=list()

        # перебираю в цикле все секции что есть в словаре
        for section in scheme_dict.keys():
            # инициализирую переменную в которой будут строки с валуями
            t=list()
            # перебираю все параметры из секции
            for param in scheme_dict[section].keys():
                # в val значение параметра а param сам параметр
                val=scheme_dict[section][param]
                # если нет значения...
                if len(val)==0 or val=='':
                    # ... то Null
                    val='Null'
                # создаю строку из dtype.id, секции, параметра и значения
                t.append('(\'%s\', \'%s\', \'%s\', \'%s\')' % (obj.name, section, param, val['data'],))
            insert.append('insert into provision_defaultconfig (dtype_id, section, param, value) values '+", ".join(t)+';')
        for query in insert:
            cursor = connection.cursor()
            cursor.execute(query)
            transaction.commit_unless_managed()
            cursor.close()

class ConfigAdmin(admin.ModelAdmin):
    list_display = ('param', 'value', 'device','section', )
    ordering = ('device','param',)
    list_filter = ('device',)
    search_fields = ('=device__mac','param','value')

class NetsAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'net' )
    ordering = ('name',)
    search_fields = ('name',)

class DefaultConfigAdmin(admin.ModelAdmin):
    list_display = ('dtype', 'section', 'param', 'value',)
    list_editable = ('section', 'param', 'value',)
    list_display_links = ('dtype',)
    ordering = ('dtype','param',)
    list_filter = ('dtype',)
    search_fields = ('param','value', 'section')

class DeviceAdmin(admin.ModelAdmin):

    def port_edit(self, *args, **kwargs):
        return u'<a href="../ports/?device=%s&ot=asc&o=4">Выбрать</a>' % (self.id,)
    port_edit.short_description = 'Порты'
    port_edit.allow_tags = True

    def cfg_edit(self, *args, **kwargs):
        return u'<a href="../configs/?device=%s">Выбрать</a>' % (self.id,)
    cfg_edit.short_description = 'Конфигурации'
    cfg_edit.allow_tags = True

    list_display = ('address', 'enable', 'state','mac', 'ip','subnet', 'sn', 'type', port_edit, cfg_edit)
    ordering = ('-state', 'address',)
    list_filter = ('enable', 'type', 'state', 'subnet')
    search_fields = ('mac', 'ip', 'sn', 'type__name', 'address__street__street', 'address__house')

    def save_model(self, request, obj, form, change):
        net = IPv4(obj.subnet.start, obj.subnet.net)
        if not net.innet(obj.ip):
            cursor = connection.cursor()
            cursor.execute('SELECT d.ip FROM public.provision_devices d, public.provision_nets n WHERE d.subnet_id = n.id AND d.subnet_id=%s' % (obj.subnet.id))
            ips=[i[0] for i in cursor.fetchall()]
            ips.append(str(obj.subnet.routers))
            print ips, obj.subnet.start
            obj.ip = net.getfree(ips, obj.subnet.start)

        mac_norm=compile('[\:\-\.\,\=\+\;\']{0,}'.join(['([0-9a-fA-F]{1,2})' for i in range(6)]))
        nmac=[i.lower() for i in mac_norm.findall(obj.mac)[0]]
        obj.mac=":".join(nmac)

        mac_check=compile('[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]')

        if len(mac_check.findall(obj.mac))==0:
            return None

        if not change:
            obj.save()

        # создаю коусор
        cursor = connection.cursor()
        # выполняю запрос где считаю портоы
        cursor.execute('select count(*) FROM provision_ports as p WHERE p.device_id = %s ;' % (obj.id,))
        if int(cursor.fetchone()[0])>0:
            # если больше 0 то сохраняю объект, считая что порты уже созданы
            cursor.close()
            # все
            return obj.save()
        else:
            # иначе просто закрываю курсор
            cursor.close()
        # Пробую открыть конфиг девайса на чтение
        try:
            filename = '%s/%s.conf' % (path.dirname(__file__)+'/scheme', obj.type_id)
            scheme=open(filename, 'r')
        except:
            # не могу открыть конфиг
            #raise Exception('FileNotFound', 'File \"%s\" not found' % (filename))
            return

        cfg=scheme.readlines()

        re=dict()
        insert=list()
        cfg_dict=dict()
        # регекс для секции
        re['section']=compile('\[(?P<section>\S+)\]\n')
        # регекс для значения
        re['data']=compile('^(?P<param>[0-9\w\_\-\+\.\,]+)=(?P<value>.{0,})\n')

        # раскуриваю конфиг
        for item in cfg:
            if re['section'].findall(item):
                section=re['section'].match(item).groupdict()['section']
                cfg_dict[section]=dict()

            if re['data'].findall(item):
                l=re['data'].findall(item)[0]
                cfg_dict[section][l[0]]=l[1]

        for section in cfg_dict.keys():
            t=list()
            t.append('(\'%s\', \'%s\')' % (section, obj.id))
            insert.append('insert into provision_ports (port, device_id) values '+", ".join(t)+';')

        for query in insert:
            cursor = connection.cursor()
            cursor.execute(query)
            transaction.commit_unless_managed()
            cursor.close()

class PortsAdmin(admin.ModelAdmin):
    def portname(obj):
        return ("порт: %s  на устройстве: %s" % (obj.port, obj.device.address))

    portname.short_description = 'Порт'

    def get_actions(self, request):
        actions = super(PortsAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    related_search_fields = {
        'user': ('name',),
    }

    def get_urls(self):
        urls = super(PortsAdmin, self).get_urls()
        my_urls = patterns('',
                            (r'^search/$', self.admin_site.admin_view(self.search))
                          )
        return my_urls + urls

    def search(self, request):
        """
        Searches in the fields of the given related model and returns the 
        result as a simple string to be used by the jQuery Autocomplete plugin
        """
        query = request.GET.get('q', None)
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        search_fields = request.GET.get('search_fields', None)

        if search_fields and app_label and model_name and query and len(query)>1:
            def construct_search(field_name):
                # use different lookup methods depending on the notation
                print field_name
                if field_name.startswith('^'):
                    return "%s__istartswith" % field_name[1:]
                elif field_name.startswith('='):
                    return "%s__iexact" % field_name[1:]
                elif field_name.startswith('@'):
                    return "%s__search" % field_name[1:]
                else:
                    return "%s__icontains" % field_name

            model = models.get_model(app_label, model_name)
            qs = model._default_manager.all()
            for bit in query.split():
                or_queries = [models.Q(**{construct_search(
                    smart_str(field_name)): smart_str(bit)})
                        for field_name in search_fields.split(',')]
                other_qs = QuerySet(model)
                other_qs.dup_select_related(qs)
                other_qs = other_qs.filter(reduce(operator.or_, or_queries))
                qs = qs & other_qs
            data = ''.join([u'%s|%s\n' % (f.__unicode__(), f.pk) for f in qs])
            return HttpResponse(data)
        return HttpResponseNotFound()

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, models.ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = ForeignKeySearchInput(db_field.rel,
                                    self.related_search_fields[db_field.name])
        return super(PortsAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    list_display = (portname, 'user', 'device', 'port')
    ordering = ('port',)
    search_fields = ('=device__ip','port','user__name')

    def config(self, obj):
        try:
            filename = '%s/%s.conf' % (path.dirname(__file__)+'/scheme', obj.device.type_id)
            conf=open(filename, 'r')
        except:
            raise Exception('FileNotFound', 'File \"%s\" not found' % (filename))

        conf=conf.readlines()
        re=dict()
        conf_dict=dict()
        re['section']=compile('\[(?P<section>\S+)\]\n')
        re['data']=compile('^(?P<param>[0-9\w\_\-\+\.\,]+)=(?P<value>.{0,})\n')

        for item in conf:
            if re['section'].findall(item):
                section=re['section'].match(item).groupdict()['section']
                conf_dict[section]=dict()

            if re['data'].findall(item):
                l=re['data'].findall(item)[0]
                conf_dict[section][l[0]]=l[1]
        return conf_dict

    def save_model(self, request, obj, form, change):
        if change:
            device = obj.device.dict()['id']
            ip = obj.device.dict()['ip']
            config = self.config(obj)

            # for eval
            enable_param = config[str(obj.port)]['enable'].split('*')[0]
            enable, disable = config[str(obj.port)]['enable'].split('*')[1].split('|')

            devuser = config[str(obj.port)]['devuser']
            devpassword = config[str(obj.port)]['devpassword']
            section = config[str(obj.port)]['section']

            if not Configs.objects.filter(device=obj.device, param=devpassword).count():
                devpassword = DefaultConfig.objects.get(dtype=obj.device.type, param = devpassword).value
            else:
                devpassword = Configs.objects.get(section = section, device=obj.device, param = devpassword).value

            login_param = config[str(obj.port)]['login']
            password_param = config[str(obj.port)]['password']

            if not isinstance(obj.user, type(None)):
                login = obj.user.name
                password = obj.user.secret
            else:
                login = ''
                password = ''

            # Если номер отвязан совсем
            if isinstance(obj.user, type(None)):
                # Проверяем были ли конфиг включения
                sql = Configs.objects.filter(device=obj.device, param=enable_param).count()
                if sql > 0:
                    # Был, чудненько, удаляем
                    query = Configs.objects.get(device=obj.device, section=section, param=enable_param)
                    query.delete()
                # Был ли логин
                sql = Configs.objects.filter(device=obj.device, param=login_param).count()
                if sql > 0:
                    # Был, чудненько, удаляем
                    query = Configs.objects.get(device=obj.device, section=section, param=login_param)
                    query.delete()
                # Был ли пароль
                sql = Configs.objects.filter(device=obj.device, param=password_param).count()
                if sql > 0:
                    # Был, чудненько, удаляем
                    query = Configs.objects.get(device=obj.device, section=section, param=password_param)
                    query.delete()
                # Чистка зависимостей

                obj.save()
                system("curl --connect-timeout 2 --digest -u %s:%s \"http://%s/admin/resync\"" % (devuser, devpassword, ip))
                return None

            # Enable port
            sql = Configs.objects.filter(device=obj.device, param=enable_param).count()
            if sql > 0:
                query = Configs.objects.get(device=obj.device, section=section, param=enable_param)
                query.value = enable
            else:
                Configs(device=obj.device, section=section, param=enable_param, value=enable).save()
            # Write login
            sql = Configs.objects.filter(device=obj.device, param=login_param).count()
            if sql > 0:
                query = Configs.objects.get(device=obj.device, section=section, param=login_param)
                query.value = login
            else:
                Configs(device=obj.device, section=section, param=login_param, value=login).save()
            # Write password
            sql = Configs.objects.filter(device=obj.device, param=password_param).count()
            if sql > 0:
                query = Configs.objects.get(device=obj.device, section=section, param=password_param)
                query.value = enable
            else:
                Configs(device=obj.device, section=section, param=password_param, value=password).save()

            obj.save()
            system("curl --connect-timeout 2 --digest -u %s:%s \"http://%s/admin/resync\"" % (devuser, devpassword, ip))
            return None

admin.site.register(Types, TypesAdmin)
admin.site.register(Configs, ConfigAdmin)
admin.site.register(DefaultConfig, DefaultConfigAdmin)
admin.site.register(Devices, DeviceAdmin)
admin.site.register(Ports, PortsAdmin)
admin.site.register(Nets, NetsAdmin)
