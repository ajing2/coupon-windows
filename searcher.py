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
from urlutils import unquote
from utils import getchar, reprDict, runCommand, OutputPath

def run(configfile, name, content, savefile):

    OutputPath.init(configFile)

    try:

        db = Database(configFile, 'specials')
        db.initialize()

        evaluation = Evaluation(configFile, db)

        data = evaluation.search(content)

        if savefile is not None:
            with open(savefile, 'w') as fp:
                fp.write(reprDict(data))
        else:
            print reprDict(data)

        return 0

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

    return -1

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    if len(sys.argv) < 3:
        print 'Usage:\n\t', sys.argv[0], 'config-file content [savefile]\n' \
            '  Or:\n\t', sys.argv[0], 'config-file \"#key#[low-price#[high-price#]] [savefile]\"\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"

    configFile = sys.argv[1]
    content = unquote(sys.argv[2])

    if len(sys.argv) > 3:
        savefile = sys.argv[3]
    else:
        savefile = None

    ret = run(configFile, name, content, savefile)

    exit(ret)

