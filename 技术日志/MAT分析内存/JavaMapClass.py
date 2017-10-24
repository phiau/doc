#!/usr/bin/python
# -*- coding: utf-8 -*-
import string


class JavaMapClass(object):
    """docstring for JavaMapClass"""

    def __init__(self, file, start):
        self.file = file
        self.start = start
        self.keyMap = {}
        self.__file2mem()
        # self.__debugInfo()
        pass

    def __debugInfo(self):
        print("size:%d" % (self.size))
        for key in self.keyMap:
            print("key:%s, num:%d" % (key, self.keyMap[key]))
        pass

    def getkeys(self):
        return self.keyMap.keys()

    def getValue(self, key):
        return self.keyMap[key]

    def __file2mem(self):
        fd = open(self.file)
        try:
            isBegin = False
            lines = fd.readlines()
            self.size = len(lines)
            for l in lines:
                if not isBegin:
                    if l.startswith(self.start):
                        isBegin = True
                        pass
                else:
                    sl = l.split()
                    if 4 == len(sl):
                        self.keyMap[sl[3]] = string.atoi(sl[1])
                        pass
                    pass
            pass
        finally:
            fd.close()
            pass
        pass
