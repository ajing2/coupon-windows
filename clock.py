#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import sys
import math

from datetime import timedelta, datetime
from utils import datetime2Seconds, reprDict

class Clock:

    def __init__(self, days=3, hourRange=(7, 21, 2)):

        today = datetime.now().replace(hour=0, minute=0,
                second=0, microsecond=0)

        self.times = list()

        for i in range(days):

            for hour in range(*hourRange):

                data = dict()

                data['time'] = today.replace(hour=hour).strftime('%Y-%m-%d %H:%M:%S')
                data['count'] = 0

                self.times.append(data)

            today += timedelta(days=1)

        self.size = len(self.times)
        self.count = 0

    def randomTime(self, startTime=None, endTime=None):

        self.count += 1

        actualSize = self.size
        avgCount = math.ceil(float(self.count) / self.size)

        if startTime is not None and endTime is not None:

            start = datetime2Seconds(startTime)
            end = datetime2Seconds(endTime)

            if start + (24 * 3600) > end:
                return startTime

            # TODO: Assume it's valid and has a long period more than 3 days

            if endTime <= self.times[0]['time']:
                return endTime

            endTime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S').replace(minute=0,
                    second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

            if endTime < self.times[self.size - 1]['time']:

                minCount = sys.maxint
                maxCount = 0

                actualSize = 0

                for data in self.times:

                    if data['time'] >= endTime:
                        break

                    count = data['count']

                    if count < minCount:
                        minCount = count

                    if count > maxCount:
                        maxCount = count

                    actualSize += 1

                if actualSize is 0:
                    return endTime # Invalid

                if minCount == maxCount:
                    avgCount = maxCount + 1
                else: # max > min
                    avgCount = maxCount

        num = random.randint(0, actualSize)

        ranges = [(num, actualSize), (0, num)]

        for aRange in ranges:

            for i in range(*aRange):

                if self.times[i]['count'] < avgCount:

                    self.times[i]['count'] += 1
                    return self.times[i]['time']

        # XXX: Should not be here
        raise Exception('Error: random {} from {} to {}'.format(num, startTime, endTime))

    def __repr__(self):
        return reprDict(self.times)

