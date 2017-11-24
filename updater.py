#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from coupon import SkuManager, CouponManager, DiscountManager
from datetime import datetime
from db import Database
from evaluation import Evaluation
from seckill import SeckillManager
from history import PriceHistoryManager
from utils import OutputPath, ThreadWritableObject

def run(configFile, name):

    OutputPath.init(configFile)
    OutputPath.clear()

    thread = ThreadWritableObject(configFile, name)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:
        db = Database(configFile, 'specials')
        db.initialize()

        skuManager = SkuManager(configFile, db)

        couponManager = CouponManager(configFile, db)
        discountManager = DiscountManager(configFile, db)
        seckillManager = SeckillManager(db)

        priceHistoryManager = PriceHistoryManager(db)
        evaluation = Evaluation(configFile, db)

        couponManager.update()
        discountManager.update()
        seckillManager.update()

        skuManager.update()
        evaluation.update()

        priceHistoryManager.update()

        evaluation.evaluate()

    except KeyboardInterrupt:
        pass
    except Exception, e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)
    finally:
        try:
            db.quit()
        except:
            pass

    thread.quit()

    thread.join()

'''
Main Entry
'''
if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    if len(sys.argv) < 2:
        print 'Usage:\n\t', sys.argv[0], 'config-file\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"

    configFile = sys.argv[1]

    run(configFile, name)

