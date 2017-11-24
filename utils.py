#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Utils
import binascii
import cStringIO
import json
import os
import pprint
import random
import re
import requests
import stat
import string
import sys
import subprocess
import threading
import time
import traceback

from datetime import tzinfo, timedelta, datetime
from selenium.webdriver.common.keys import Keys

def seconds2Datetime(seconds):
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

def datetime2Seconds(dt):
    return time.mktime(datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').timetuple())
    # return (datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - datetime(1970, 1, 1)).total_seconds() # XXX CTS

def randomSleep(minS, maxS):
    time.sleep(random.uniform(minS, maxS))

def mkdir(path, mode=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH):
    if not os.path.exists(path):
        os.mkdir(path, mode)

def chmod(path, mode=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH):
    if os.path.exists(path):
        os.chmod(path, mode)

def getchar():
    print 'Please press return key to continue'
    sys.stdin.read(1)

def atoi(src):
    n = 0
    for c in src.lstrip():
        if c.isdigit():
            n *= 10
            n += int(c)
        else:
            break
    return n

def inputElement(element, content, normalSpeed=(0.1, 0.2), slowSpeed=(0.2, 0.4)):

    def randomChar():
        return random.choice(string.ascii_lowercase + string.digits)

    def sendChar(element, ch):
        element.send_keys(ch)

    def removeChar(element):
        element.send_keys(Keys.BACK_SPACE)

    # Type: 0, digit; 1, alpha; 2, space; 3, other
    cLastType = 1

    # Simulation of human input, sometime typo.
    for c in content:

        if c.isdigit():
            cType = 0
        elif c.isalpha():
            cType = 1
        elif c.isspace():
            cType = 2
        else:
            cType = 3

        if cType is not cLastType:

            num = random.randint(0, 2)
            isDelay = (num < 2)

            speed = slowSpeed
            typoThresholdValue = 3

        else:
            speed = normalSpeed
            typoThresholdValue = 1

        randomSleep(speed[0], speed[1])

        # Three times typo at most
        for i in range(0, 3):

            num = random.randint(0, 9)
            isTypo = (num < typoThresholdValue)

            if not isTypo:
                break

            # Typo
            ch = randomChar()
            sendChar(element, ch)
            randomSleep(normalSpeed[0], normalSpeed[1])

            # Remove
            removeChar(element)
            randomSleep(speed[0], speed[1])

        sendChar(element, c)

def toVisibleAscll(src):

    if None == src or 0 == len(src):
        return src

    if unicode != type(src):
        try:
            src = unicode(src, errors='ignore')
        except TypeError, e:
            print 'Unable to translate {!r} of type {}'.format(src, type(src)), ':', e

    dest = ''

    for char in src:
        if char < unichr(32): continue
        dest += char

    return dest

def hexlifyUtf8(src):
    return binascii.hexlify(src.encode('utf-8', 'ignore'))

def unhexlifyUtf8(src):
    return binascii.unhexlify(src).decode('utf-8', 'ignore')

def runCommand(cmd, shell=False):

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output, unused_err = process.communicate()
    retcode = process.poll()

    if retcode is not 0:
        raise subprocess.CalledProcessError(retcode, cmd)

    return retcode

# update property of name to value
def updateProperty(path, name, value):
    fp = None
    targetLine = None
    newLine = None
    try:
        fp = open(path)
        minlen = len(name) + 1
        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue
            group = line.strip().split('=')
            if 2 != len(group) or group[0].strip() != name:
                continue
            if group[1] == value:
                return None
            else:
                targetLine = line
                newLine = '{}={}\r\n'.format(name,value)
                break
    except IOError:
        pass
    finally:
        if fp != None: fp.close()

    if targetLine != None and newLine != None:
        with open(path) as fp:
            content = fp.read()

        content = content.replace(targetLine, newLine)

        with open(path, 'w') as fp:
            fp.write(content)

    return None

def getProperty(path, name):

    fp = None

    try:
        fp = open(path)

        minlen = len(name) + 1

        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue

            line = line.strip()
            pos = line.find('=')

            if pos < 0:
                continue

            if line[:pos] != name:
                continue

            return line[pos+1:].strip()

    except IOError:
        pass

    finally:
        if fp != None: fp.close()

    return None

def safePop(obj, name, defaultValue=None):

    try:
        return obj.pop(name)
    except KeyError:
        pass

    return defaultValue

def getMatchString(content, pattern):

    matches = re.findall(pattern, content)

    if matches is None or 0 == len(matches):
        return None

    return matches[0]

def dump(obj):

    def dumpObj(obj):

        fields = ['    {}={}'.format(k, v)
            for k, v in obj.__dict__.items() if not k.startswith('_')]

        return ' {}:\n{}'.format(obj.__class__.__name__, '\n'.join(fields))

    if obj is None: return None

    if type(obj) is list:

        for subObj in obj:
            dump(subObj)
    else:
        print dumpObj(obj)

def reprDict(data):
    return json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)

def printDict(obj):
    UniPrinter().pprint(obj)

class UniPrinter(pprint.PrettyPrinter):

    def format(self, obj, context, maxlevels, level):

        if isinstance(obj, unicode):

            out = cStringIO.StringIO()
            out.write('u"')

            for c in obj:
                if ord(c) < 32 or c in u'"\\':
                    out.write('\\x%.2x' % ord(c))
                else:
                    out.write(c.encode("utf-8"))

            out.write('"''"')

            # result, readable, recursive
            return out.getvalue(), True, False

        if isinstance(obj, str):

            out = cStringIO.StringIO()
            out.write('"')

            for c in obj:
                if ord(c) < 32 or c in '"\\':
                    out.write('\\x%.2x' % ord(c))
                else:
                    out.write(c)

            out.write('"')

            # result, readable, recursive
            return out.getvalue(), True, False

        return pprint.PrettyPrinter.format(self, obj,
            context, maxlevels, level)

# XXX: Gentlemen should not force ladies to quit but ask them to quit.
class LadyThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            # self.runOnce()

            self.mutex.release()

        print 'Quit'

    def runOnce(self):
        raise TypeError('No implement')

    def sleep(self, seconds):

        while self.running and seconds > 0:
            seconds -= 1
            time.sleep(1)

    def quit(self):

        print 'Stopping ...'
        self.running = False

class AutoReleaseThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def initialize(self):

        try:
            self.mutex.acquire()

            if not self.isInitialized:

                self.isInitialized = True

                self.onInitialized()

            self.accessTime = time.time()

        except KeyboardInterrupt:
            raise KeyboardInterrupt

        finally:
            self.mutex.release()

    def release(self):

        self.isInitialized = False

        self.onReleased()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if self.isInitialized:

                diff = time.time() - self.accessTime

                if diff > 30: # 30 seconds
                    self.release()

            self.mutex.release()

            time.sleep(1)

        else:
            self.release()

        print 'Quit'

    def quit(self):

        print 'Stopping ...'
        self.running = False

class OutputPath:

    LOG_OUTPUT_PATH = None
    DATA_OUTPUT_PATH = None
    AUTH_OUTPUT_PATH = None

    @staticmethod
    def init(configFile):

        outputPath = getProperty(configFile, 'output-path')
        outputPath = os.path.realpath(outputPath)

        mkdir(outputPath)

        OutputPath.LOG_OUTPUT_PATH = os.path.join(outputPath, 'logs')
        mkdir(OutputPath.LOG_OUTPUT_PATH)

        OutputPath.DATA_OUTPUT_PATH = os.path.join(outputPath, 'datas')
        mkdir(OutputPath.DATA_OUTPUT_PATH)

        OutputPath.AUTH_OUTPUT_PATH = os.path.join(outputPath, 'auths')
        mkdir(OutputPath.AUTH_OUTPUT_PATH)

        OutputPath.SHARE_OUTPUT_PATH = os.path.join(outputPath, 'shares')
        mkdir(OutputPath.SHARE_OUTPUT_PATH)

    @staticmethod
    def getDataPath(key, suffix):
        return '{}/{}.{}'.format(OutputPath.DATA_OUTPUT_PATH, key, suffix)

    @staticmethod
    def getAuthPath(name):
        return '{}/{}.png'.format(OutputPath.AUTH_OUTPUT_PATH, name)

    @staticmethod
    def getSharePath():
        return '{}/{}.json'.format(OutputPath.SHARE_OUTPUT_PATH, datetime.now().strftime('%Y_%m_%d_%H'))

    @staticmethod
    def clear():

        # Data
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 47 * 3600, '.js') # Almost two days overdue
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 23 * 3600, '.json') # Almost one day overdue
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 23 * 3600, '.html') # Almost one day overdue
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 23 * 3600, '.png') # Almost one day overdue

        # Auth
        removeOverdueFiles(OutputPath.AUTH_OUTPUT_PATH, 23 * 3600, '.png') # Almost one day overdue

class ThreadWritableObject(threading.Thread):

    def __init__(self, configFile, name):

        threading.Thread.__init__(self)

        self.running = True

        self.path = os.path.join(OutputPath.LOG_OUTPUT_PATH, '{}.log'.format(name))
        self.contents = []

        self.mutex = threading.Lock()

    def write(self, content):

        self.mutex.acquire()

        self.contents.append(content)

        self.mutex.release()

    def run(self):

        def output(path, contents):

            with open(path, 'a') as fp:

                for content in contents:
                    fp.write(content)

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if 0 != len(self.contents):

                MAX_SIZE = 2*1024*1024

                if os.path.exists(self.path) and os.stat(self.path).st_size > MAX_SIZE:

                    os.rename(self.path, '{}.old'.format(self.path))

                output(self.path, self.contents)

                del self.contents[:]

            self.mutex.release()

            time.sleep(10)

        else:
            output(self.path, self.contents)

    def quit(self):

        print 'Quit ...'
        self.running = False

def removeOverdueFiles(pathname, seconds, suffix=None):

    now = time.time()

    for parent, dirnames, filenames in os.walk(pathname):

        for filename in filenames:

            path = os.path.join(parent, filename)

            if None != suffix and not filename.endswith(suffix):
                continue

            if now > os.path.getctime(path) + seconds:
                # Remove
                os.remove(path)
