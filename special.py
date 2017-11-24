#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

from base import SpecialFormatter
from datetime import datetime
from imgkit import ImageKit
from network import Network
from qwd import QWD
from utils import getProperty, OutputPath

class Searcher:

    def __init__(self, configFile):

        self.qwd = QWD(configFile)

        self.url = getProperty(configFile, 'search-url')
        self.configFile = configFile

    def search(self, content):

        r = Network.post(self.url, data={'content': content})

        if r is None:
            print 'No result for', content
            return False

        try:
            obj = json.loads(r.content.decode('utf-8', 'ignore'))
        except ValueError as e:
            print 'Error (', e, ') of json: "', r.content, '"'
            return False

        num = obj['num']
        if num is 0:
            print 'Error content: "', r.content, '"'
            return False

        print 'Found', num, 'SKU with "', content, '"'

        datas = obj['list']

        plates = list()
        urls = list()

        for data in datas:

            formatter = SpecialFormatter.create(data)

            plate = formatter.getPlate(self.qwd)
            url = data['skuimgurl']

            plates.append(plate)
            urls.append(url)

        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        path = OutputPath.getDataPath('search_{}'.format(now), 'jpeg')

        self.plate = '\n----------------------------\n'.join(plates)
        self.image = ImageKit.concatUrlsTo(path, urls)

        return True

