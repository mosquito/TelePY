#!/usr/bin/env python
# encoding: utf-8
"""
gtexttospeech.py

Created by Paul Bagwell on 2011-03-08.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

import collections
import io
import os
import sys
import textwrap
import urllib2
from codecs import open as uopen
from cookielib import CookieJar
from shutil import copyfileobj
from tempfile import mkstemp
from urllib import pathname2url


__all__ = ['TextToSpeech', 'TextToSpeechError']


class TextToSpeechError(Exception):
    pass


class TextToSpeech(object):
    substitutions = (  # list of substitutions
        (u'ё', u'йо'),
        (u'трех', u'трьох'),
        (u'хабрахабр', u'хабрах+абр'),
    )
    headers = (
        ('Host', 'translate.google.com'),
        ('User-Agent', ('Mozilla/5.0 (Windows; U; Windows NT 6.1;'
            ' en-US; rv:2.0.0) Gecko/20110320 Firefox/4.0.0')),
        ('Accept', 'text/html,application/xhtml+xml,'
            'application/xml;q=0.9,*/*;q=0.8'),
        ('Accept-Language', 'en-us,en;q=0.5'),
        ('Accept-Encoding', 'gzip,deflate'),
        ('Accept-Charset', 'utf-8;q=0.7,*;q=0.7'),
    )

    def __init__(self, *inputs, **kwargs):
        self.language = kwargs.get('language', 'ru')
        if isinstance(kwargs.get('substitutions'), collections.Iterable):
            self.substitutions = substitutions
        buf = ''.join(
            stream.read() if isinstance(stream, file) else str(stream)
            for stream in inputs
        )

        self.buffer = self.split(buf.decode('utf-8'))
        self.opener = self.make_opener()
        self.files = []

    def make_opener(self):
        handler = urllib2.HTTPCookieProcessor(CookieJar())
        opener = urllib2.build_opener(handler)
        opener.addheaders = self.headers
        return opener

    def urls(self):
        """Generates url to Google Translate MP3 file."""
        tpl = u'http://translate.google.com/translate_tts?q=[{0}]&tl={1}'
        for line in self.buffer:
            yield tpl.format(pathname2url(line.encode('utf-8')), self.language)

    def split(self, buf, length=95):
        """Splits files by sentences with maximum length=length."""
        for fr, to in self.substitutions:
            buf = buf.replace(fr, to)
        return textwrap.wrap(buf, length, break_long_words=True)

    def download_voices(self):
        """Downloads MP3s."""
        for url in self.urls():
            # print url
            fd, path = mkstemp('.mp3')
            fd = os.fdopen(fd, 'wb+')
            try:
                page = self.opener.open(url)
            except urllib2.HTTPError:
                raise TextToSpeechError('Google blocked your computer. '
                    'To unblock it, follow this link: {0}'.format(page.url))
            copyfileobj(page, fd)
            fd.seek(0)
            self.files.append((path, fd))

    def delete_voices(self):
        """Deletes all downloaded files."""
        while self.files:
            path = self.files.pop()[0]
            os.unlink(path)

    def join_voices(self, to):
        """Copies audiodata from all downloaded MP3s to result_file."""
        first = True
        if not isinstance(to, file):
            to = open(to, 'wb')
        while self.files:
            path, fd = self.files.pop(0)
            if not first:  # MP3 header
                fd.seek(32, 1)
            copyfileobj(fd, to)
            os.unlink(path)
            first = False
        return to

    def create(self, result):
        """Downloads all voices and copies them to result_file."""
        self.download_voices()
        return self.join_voices(result)
