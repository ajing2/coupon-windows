# -*- coding:utf-8 -*-

import json

from network import Network
from utils import getMatchString, OutputPath

def getSlogan(skuid):

    path = OutputPath.getDataPath(skuid, 'html')

    SKU_MAIN_URL_TEMPLATE = 'http://item.m.jd.com/product/{}.html'
    url = SKU_MAIN_URL_TEMPLATE.format(skuid)

    ret = Network.saveGetUrl(path, url)
    #print 'Update', path, ':', ret

    if ret < 0:
        return None

    #PATTERN = r'<div class="prod-act">(.*?)</div>'
    PATTERN = r'<div class="prod-act">(.*?)<'

    with open(path) as fp:
        content = fp.read()

        slogan = getMatchString(content, PATTERN)
        if slogan is not None and not isinstance(slogan, unicode):
            slogan = unicode(slogan, errors='ignore')
        return slogan

    return None

def getComments(skuid):

    COMMENT_URL_TEMPLATE = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId={}'
    url = COMMENT_URL_TEMPLATE.format(skuid)

    path = OutputPath.getDataPath(skuid, 'json')

    ret = Network.saveGetUrl(path, url)
    #print 'Update', path, ':', ret

    if ret < 0:
        return None

    with open(path) as fp:
        content = fp.read()
        obj = json.loads(content)
        return obj.pop('wareDetailComment')

    return None

