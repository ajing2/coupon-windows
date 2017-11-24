#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from base import SpecialFormatter
from datetime import datetime
from db import Database
from evaluation import Evaluation
from qwd import QWD
from utils import getchar, getProperty, reprDict, runCommand, OutputPath, ThreadWritableObject

def run(configfile, name):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name)
    thread.start()

    sys.stdout = thread
    sys.errout = thread # XXX: Actually, it does NOT work

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        qwd = QWD(configFile)

        evaluation.updateOverdue()

        path = OutputPath.getSharePath()
        sharePath = getProperty(configFile, 'output-share-file')

        cmd = '/bin/rm -f {1} && /bin/ln -s {0} {1}'.format(path, sharePath)
        runCommand(cmd)

        data = evaluation.output()

        with open(path, 'w') as fp:
            fp.write(reprDict(data))

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

