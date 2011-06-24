#-*- coding: utf-8 -*-
from django.db import *

class sqlitem:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class select:
    def __init__(self, query, fields):
        self.__cursor = connection.cursor()
        self.__cursor.execute(query)
        fetch = self.__cursor.fetchall()
        row = list()
        self.__keys = list()
        if not len(fetch)==0:
            for i in fetch:
                keys = dict()
                for k in range(0,len(fields)):
                    keys[fields[k]]=i[k]
                row.append(sqlitem(**keys))
                self.__keys.append(keys)
        self.objects = row

    def __del__(self):
        self.__cursor.close()
        
