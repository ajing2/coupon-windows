import json

from base import Sku, PromotionHistory, PriceHistoryData
from js import JsExecutor
from network import Network
from utils import OutputPath

class PriceHistoryManager:

    def __init__(self, db=None):
        self.priceHistoryDataList = None
        self.db = db

        self.executor = JsExecutor('js/huihui.js')

    def update(self):

        tableNames = ['SkuTable']

        for tableName in tableNames:
            self.updateHistory(tableName)

    def updateHistory(self, tableName):

        sql = 'SELECT id FROM HistoryTable LIMIT 1'
        result = self.db.query(sql)

        sql = 'SELECT skuid, title FROM {}'.format(tableName)
        where = ' WHERE skuid NOT IN (SELECT skuid FROM HistoryTable) '

        if result is not None:
            sql += where

        result = self.db.query(sql)

        if result is None:
            return

        for row in result:

            if self.priceHistoryDataList is None:
                self.priceHistoryDataList = list()

            priceHistoryData = self.create(row)
            self.priceHistoryDataList.append(priceHistoryData)

    def create(self, data):

        skuid = data['skuid']

        if self.db is not None and self.db.findOne('HistoryTable', skuid=skuid):
            # Already exists
            return None

        title = data['title']

        priceHistoryData = PriceHistoryManager.getPriceHistoryData(self.executor, data)

        if priceHistoryData is None:
            return None

        priceHistoryData.insert(self.db, 'HistoryTable')

        return priceHistoryData

    @staticmethod
    def getPriceHistoryData(executor, data):

        skuid = data['skuid']
        title = data['title']

        url = 'http://item.jd.com/{}.html'.format(skuid) # For history searching
        # Get URL for price history
        url = executor.context.requestPriceInfo(title, url)

        # Get price histories
        path = OutputPath.getDataPath(skuid, 'js')

        ret = Network.saveHttpData(path, url)
        #print 'Update', path, ':', ret, ':', title

        if ret < 0:
            return None

        obj = PriceHistoryManager.parse(path)
        if obj is None:
            return None

        return PriceHistoryManager.generatePriceHistoryData(data, obj)

    @staticmethod
    def parse(path):

        def getJsonString(path):

            try:
                with open(path) as fh:
                    for line in fh.readlines(): 
                        if len(line) > 1024:

                            start = line.find('{')
                            end = line.rfind('}')

                            return line[start:end+1]
            except IOError:
                pass

            return None

        data = getJsonString(path)

        if not data:
            print 'Wrong format: {}'.format(path)
            return None

        return json.loads(data)

    @staticmethod
    def generatePriceHistoryData(data, obj):

        priceHistoryData = None
        promotionHistoryList = None

        if 'promotionHistory' in obj.keys():
            for promotionHistory in obj['promotionHistory']:
                if promotionHistoryList is None:
                    promotionHistoryList = list()

                promotionHistoryList.append(PromotionHistory(promotionHistory))

        if 'priceHistoryData' in obj.keys():

            priceHistory = obj['priceHistoryData']
            priceHistory['skuid'] = data['skuid']

            priceHistoryData = PriceHistoryData(priceHistory)
            priceHistoryData.updatePromotion(promotionHistoryList)

            priceHistoryData.data['list'] = json.dumps(priceHistoryData.data.pop('list'),
                    ensure_ascii=False, indent=4, sort_keys=True)

        return priceHistoryData

