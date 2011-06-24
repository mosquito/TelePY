#-*- coding: utf-8 -*-
from django.db.models import *
from settings import ASTERISK_AUDIO_FILES as AAF
from os import path
from pytils.translit import slugify

class SndFile(Model):
    aster_path = CharField(max_length=256, editable=False, verbose_name=u'путь для asterisk', primary_key=True)
    title = CharField(max_length=80, editable=True, default='unnamed file', verbose_name=u'название', db_index=True)
    comment = TextField(editable=True, null=True, blank=True, verbose_name=u'комментарий', db_index=True)
    source = FileField(upload_to='%s/source' % AAF, editable=True, blank=True, null=True, verbose_name='Source file')
    wav = FileField(upload_to=AAF, editable=False, null=True, verbose_name='wav format')
    alaw = FileField(upload_to=AAF, editable=False, null=True, verbose_name='alaw format')
    gsm = FileField(upload_to=AAF, editable=False, null=True, verbose_name='gsm format')

    def __unicode__(self):
        return self.title

    def __init__(self,*args, **kwargs):
        super(SndFile,self).__init__(*args, **kwargs)
        self.old_source = self.source
    def save(self, *args, **kwargs):
        self.aster_path = path.join(AAF,slugify(self.title))
        super(SndFile,self).save(*args,**kwargs)

    def delete(self,*args,**kwargs):
        self.source.delete()
        self.wav.delete()
        self.alaw.delete()
        self.gsm.delete()
        super(SndFile,self).delete(*args,**kwargs)

    class Meta:
        unique_together=('title',)
        ordering = ['title',]
        verbose_name = "Sound file"
        verbose_name_plural = "Sound files"
