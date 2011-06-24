#!/usr/bin/python
#-*- coding: utf-8 -*-

from gtexttospeech import TextToSpeech as TTS
from tempfile import NamedTemporaryFile

def tts_file(text, lang='ru'):
    f = NamedTemporaryFile(suffix='.mp3')
    TTS(text, language=lang).create(f.name)
    return f

def tts_data(text, lang='ru'):
    f = NamedTemporaryFile(suffix='.mp3')
    TTS(text, language=lang).create(f.name)
    data = f.file.read()
    f.close()
    return data

if __name__=='__main__':
    from sys import argv
    from os import system

    sound = tts_file(argv[1])
    if system("mplayer %s" % sound.name):
        print sound.file.read()
    sound.close()
