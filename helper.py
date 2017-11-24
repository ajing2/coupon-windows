#!/usr/bin/env python
# -*- coding:utf-8 -*-

import itchat
import os
import sys
import time
import traceback

from datetime import datetime
from wx import WX
from utils import OutputPath, ThreadWritableObject

def run(configFile, name, uuid):

    wx = None

    @itchat.msg_register(itchat.content.TEXT)
    def text(msg):
        wx.text(msg)

    @itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
    def text(msg):
        wx.textGroup(msg)

    def quit():
        try:
            wx.quit()
        except:
            pass

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        wx = WX(configFile)
        wx.login(quit, uuid)
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)
    finally:
        quit()

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 2:
        print 'Usage:\n\t', sys.argv[0], 'config-file [uuid]\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    # time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"
    configFile = sys.argv[1]

    if len(sys.argv) > 2:
        uuid = sys.argv[2]
    else:
        uuid = None

    run(configFile, name, uuid)

