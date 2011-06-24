from django.shortcuts import render_to_response as render
from django.db import connection
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseNotFound
from re import compile
from datetime import datetime as dt
from provision.models import *
from django.shortcuts import get_object_or_404
from ipaddr import IPv4
from sql import select

class Dict(dict):
    def __new__(cls, *args, **kwargs):
        self = dict.__new__(cls, *args, **kwargs)
        self.__dict__ = self
        return self

def provision(request, alias, mac, sn, *args, **kwargs):
    mac_norm=compile('[\:\-\.\,\=\+\;\']{0,}'.join(['([0-9a-fA-F]{1,2})' for i in range(6)]))
    nmac=[i.lower() for i in mac_norm.findall(mac)[0]]
    nmac=":".join(nmac)

    if not Devices.objects.filter(enable=True, mac=nmac, sn=sn).count():
        return HttpResponseNotFound()

    obj = Devices.objects.get(enable=True, mac=nmac, sn=sn)
    config = DefaultConfig.objects.filter(dtype=obj.type)

    data=dict()

    for i in config:
        data[i.section] = dict()

    for i in config:
        value = i.value
        try:
            if 'Null' in value:
                value = ''
        except:
            value = ''
        data[i.section][i.param] = value

    config = Configs.objects.filter(device=obj).all()

    for i in config:
        value = i.value
        if 'Null' in value:
            value = ''
        data[i.section][i.param] = value

    outdata = Dict()

    for section in data.keys():
        outdata[section.lower().replace(" ", '_')]=Dict()

        for param, value in data[section].items():
            outdata[section.lower().replace(" ", '_')][param.lower().replace(' ', '_')] = value

    return render(obj.type.template, {'data': outdata,'date': dt.now()}, mimetype='text/plain')

def dns(request, *args, **kwargs):
    cursor = connection.cursor()
    date = dt.now()
    query = " SELECT p.user_id, d.ip FROM provision_ports p, provision_devices d WHERE p.device_id = d.id AND p.user_id IS NOT NULL  AND p.user_id not LIKE '%%l%%' order by d.ip"
    names = select(query, ('name', 'ip'))
    cursor.close()
    return render('dns.zone', {'names': names.objects, 'date': date, 'serial': ("%02d" % ((date.hour*date.minute+15)/15)) }, mimetype='text/plain')

def dhcp(request, *args, **kwargs):
    nets = Nets.objects.all()
    for net in nets:
        setattr(net, "ipv4", IPv4(net.start, net.net))
    return render('dhcpd.conf', {'data': Devices.objects.all(), 'nets': nets }, mimetype='text/plain')

