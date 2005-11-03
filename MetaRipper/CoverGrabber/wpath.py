#!/usr/bin/python2.4

import os, sys, copy

class dummy(object):
    settingIOEncoding = 'utf-8'

class wpath(object):
    '''This class wraps the open, os.listdir and commonly used filepath related methods. Each of the
       wrapped functions will decide if it needs to call the underlying functions with a unicode
       string, or some user chosen encoding.'''

    def __init__(self, config = dummy()):
        self.config = config

    def toUnicode(self, str):

        try:
            return unicode(str, self.config.settingIOEncoding)
        except UnicodeError:
            try:
                return unicode(str, "iso-8859-1")
            except UnicodeError:
                return u"[ filename encoding not recognized ]"

    def toStr(self, ustr):
        return ustr.encode(self.config.settingIOEncoding, 'replace')

    def open(self, file, mode):
        if sys.platform == "win32":
            return open(file, mode)
        else:
            return open(self.toStr(file), mode)

    def stat(self, file):
        if sys.platform == "win32":
            return os.stat(file)
        else:
            return os.stat(self.toStr(file))

    def basename(self, file):
        if sys.platform == "win32":
            return os.path.basename(file)
        else:
            return self.toUnicode(os.path.basename(self.toStr(file)))

    def dirname(self, file):
        if sys.platform == "win32":
            return os.path.dirname(file)
        else:
            return self.toUnicode(os.path.dirname(self.toStr(file)))

    def abspath(self, file):
        if sys.platform == "win32":
            return os.path.abspath(file)
        else:
            return self.toUnicode(os.path.abspath(self.toStr(file)))

    def isdir(self, file):
        if sys.platform == "win32":
            return os.path.isdir(file)
        else:
            return os.path.isdir(self.toStr(file))

    def isfile(self, file):
        if sys.platform == "win32":
            return os.path.isfile(file)
        else:
            return os.path.isfile(self.toStr(file))

    def islink(self, file):
        if sys.platform == "win32":
            return os.path.islink(file)
        else:
            return os.path.islink(self.toStr(file))

    def access(self, file, mode):
        if sys.platform == "win32":
            return os.access(file, mode)
        else:
            return os.access(self.toStr(file), mode)

    def split(self, file):
        if sys.platform == "win32":
            return os.path.split(file)
        else:
            return [ self.toUnicode(x) for x in os.path.split(self.toStr(file)) ]

    def join(self, *args):
        if sys.platform == "win32":
            return os.path.join(*args)
        else:
            return self.toUnicode(os.path.join(*[ self.toStr(x) for x in copy.copy(args) ]))

    def listdir(self, path):
        if sys.platform == "win32":
            return os.listdir(path)
        else:
            return [ self.toUnicode(x) for x in os.listdir(self.toStr(path)) ]
