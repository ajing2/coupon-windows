#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import time
import requests

from qwd import QWD
from base import SpecialFormatter
from utils import datetime2Seconds, getProperty, LadyThread

class Schedule(LadyThread):

    def __init__(self, configFile):

        LadyThread.__init__(self)

        self.qwd = QWD(configFile)

        self.url = getProperty(configFile, 'share-url')
        self.imageType = int(getProperty(configFile, 'share-image-type'))

        self.isUpdateNeeded = True

    def update(self):

        r = requests.get(self.url)
        obj = json.loads(r.content)

        print 'Updated', obj['num'], 'SKU between', obj['startTime'], 'and', obj['endTime']

        self.num = obj.pop('num')

        if self.num is 0:
            return False

        startTime = datetime2Seconds(obj.pop('startTime'))
        endTime = datetime2Seconds(obj.pop('endTime'))

        self.interval = (endTime - startTime) / self.num

        self.index = 0
        self.dataList = obj.pop('list')

        self.isUpdateNeeded = False

        return True

    def runOnce(self):

        if self.isUpdateNeeded:
            updated = self.update()

            if not updated:
                self.sleep(1800) # Half an hour
                return

        if self.index == self.num:
            self.isUpdateNeeded = True
            return

        data = self.dataList[self.index]
        self.index += 1

        startTs = time.time()

        formatter = SpecialFormatter.create(data)

        plate = formatter.getPlate(self.qwd)
        image = formatter.getImage(self.imageType)

        self.send(plate, image)

        endTs = time.time()

        interval = self.interval - endTs + startTs

        if interval > 0:
            self.sleep(interval)

    def send(self, plate, image):
        raise TypeError('No implement')

