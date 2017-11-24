#!/usr/bin/env python
# -*- coding:utf-8 -*-

import itchat
import random
import sys
import time

def nap(s):
    s = float(s)
    hs = s / 2
    time.sleep(random.uniform(hs, s + hs))

def output_info(msg):
    print('[INFO] %s' % msg)

def output_error(msg):
    print('[ERROR] %s' % msg)

def getUuid(uuidPath):

    for i in range(10):

        output_info('Getting uuid %d' % i)

        uuid = itchat.get_QRuuid()
        if uuid is not None:

            with open(uuidPath, 'w') as fp:
                fp.write(uuid)

            return uuid

        nap(2) # Sleep a while

    return None

def getAuthQr(uuid, qrPath):

    output_info('Getting QR Code')

    return itchat.get_QR(uuid, picDir=qrPath, enablePrintQR=False)

def run(uuidPath, qrPath):

    for i in range(10):

        output_info('Update QR code %d' % i)

        uuid = getUuid(uuidPath)

        if uuid is None:
            ret = 10
            nap(2) # Sleep a while
            continue

        if not getAuthQr(uuid, qrPath):
            ret = 11
            nap(2) # Sleep a while
            continue

        break

    else:
        output_error('Failed to get QR Code, please restart the program')
        return ret

    output_info('Please scan the QR Code')
    return 0

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 3:
        print 'Usage:\n\t', sys.argv[0], 'uuid-path qr-path\n'
        exit(1)

    uuidPath = sys.argv[1]
    qrPath = sys.argv[2]

    ret = run(uuidPath, qrPath)
    exit(ret)

