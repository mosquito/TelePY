#-*- coding: utf-8 -*-
from django.contrib import admin
from pytils.translit import slugify
from asterfiles.models import SndFile
from settings import ASTERISK_AUDIO_FILES as AAF
from os import system, path, chmod
import stat
from django.core.files import File
from django import forms
from tempfile import NamedTemporaryFile
from gTTS import tts_file

class SndFileAdmin(admin.ModelAdmin):
    def linkplay(self):
        return u'<a href="#" onClick="set(\'/sounds/source/%s\', \'%s\', $(this)); return false;">%s <img src="/media/img/play.png" alt="" style="float: right;"/></a>' % (self.source.name.split('/')[-1], self.title, self.title)
    linkplay.allow_tags = True
    linkplay.short_description = u'Название'
    list_display = (linkplay, 'comment')
    list_display_links = ('comment',)
    search_fields = ('title', 'comment')
    fieldsets = ((None, {'fields': (('title', 'source'), 'comment' ),}),)

    def save_model(self, request, obj, form, change):
        if request.FILES.has_key('source'):
            # change source name
            obj.wav.delete()
            obj.alaw.delete()
            obj.gsm.delete()
            obj.source.delete()
            obj.old_source.delete()
            obj.save()
            raw_name = "%s" % (slugify(obj.title))

            # get path source
            source = request.FILES['source'].temporary_file_path()
            print source
            f = NamedTemporaryFile(suffix='.wav')

            # CONVERT TO WAV
            if system("""sox -q %s -r 8000 -c 1 -s %s \
                    compand 0.02,0.05 -60,-60,-30,-10,-20,-8,-5,-8,-2,-8 -8 -7 0.05 \
                    resample -ql""" % (source, f.name)) != 0:
                raise form.ValidationError('Not converting to WAV')
            # open result wav
            obj.wav = File(f)
            obj.wav.name = "%s.wav" % raw_name
            obj.save()

            alaw = NamedTemporaryFile(suffix='.alaw')
            chmod(alaw.name, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            gsm = NamedTemporaryFile(suffix='.gsm')
            chmod(gsm.name, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            # converting by asterisk
            chmod(f.name, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            if system("""sudo /usr/sbin/asterisk -rx 'file convert %s %s'"""  % (f.name, alaw.name)):
                raise form.ValidationError('Not converting to ALAW')
            if system("""sudo /usr/sbin/asterisk -rx 'file convert %s %s'"""  % (f.name, gsm.name)):
                raise form.ValidationError('Not converting to GSM')

            obj.alaw = File(alaw)
            obj.alaw.name = "%s.alaw" % raw_name
            obj.gsm = File(gsm)
            obj.gsm.name = "%s.gsm" % raw_name
            obj.save()
            mp3 = NamedTemporaryFile(suffix='.mp3')
            if system("""lame -m m --cbr -b 64 --resample 16 --bitwidth 16 %s %s""" % (f.name, mp3.name)):
                raise form.ValidationError('Not converting to MP3')
            obj.source = File(mp3)
            obj.source.name = "%s.mp3" % (raw_name,)
            obj.save()
        elif not obj.aster_path and obj.comment.__len__():
            # get path source
            obj.save()
            text2speech = obj.comment.encode('utf-8','ignore')
            gtts = tts_file(text2speech)
            source = gtts.name
            f = NamedTemporaryFile(suffix='.wav')

            # CONVERT TO WAV
            if system("""sox -q %s -r 8000 -c 1 -s %s \
                    compand 0.02,0.05 -60,-60,-30,-10,-20,-8,-5,-8,-2,-8 -8 -7 0.05 \
                    resample -ql""" % (source, f.name)) != 0:
                raise form.ValidationError('Not converting to WAV')
            # open result wav
            raw_name = "%s" % (slugify(obj.title))
            obj.wav = File(f)
            obj.wav.name = "%s.wav" % raw_name
            obj.save()

            alaw = NamedTemporaryFile(suffix='.alaw')
            chmod(alaw.name, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            gsm = NamedTemporaryFile(suffix='.gsm')
            chmod(gsm.name, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            # converting by asterisk
            chmod(f.name, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            if system("""sudo /usr/sbin/asterisk -rx 'file convert %s %s'"""  % (f.name, alaw.name)):
                raise form.ValidationError('Not converting to ALAW')
            if system("""sudo /usr/sbin/asterisk -rx 'file convert %s %s'"""  % (f.name, gsm.name)):
                raise form.ValidationError('Not converting to GSM')

            obj.alaw = File(alaw)
            obj.alaw.name = "%s.alaw" % raw_name
            obj.gsm = File(gsm)
            obj.gsm.name = "%s.gsm" % raw_name
            obj.save()
            mp3 = NamedTemporaryFile(suffix='.mp3')
            if system("""lame -m m --cbr -b 64 --resample 16 --bitwidth 16 %s %s""" % (f.name, mp3.name)):
                raise form.ValidationError('Not converting to MP3')
            obj.source = File(mp3)
            obj.source.name = "%s.mp3" % (raw_name,)
            obj.save()
        else:
            obj.save()


admin.site.register(SndFile, SndFileAdmin)
