#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Url utils
import json
import re
import requests

from network import Network
from urllib import unquote_plus as urlunquote
from utils import getProperty

def unquote(src):

    if not isinstance(src, str):
        return src

    try:
        return urlunquote(src).decode('utf-8', 'ignore')
    except:
        pass

    return src

class UrlUtils:

    SHORT_URL_TRANSLATOR_URL = ''
    SHORT_URL_REFERER = ''
    SHORT_URL_USER_AGENT = ''
    SHORT_URL_SOURCE = ''
    SHORT_URL_CALLBACK = ''

    HTTP_URL_PATTERN = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    HTTP_SHORT_URL_PATTERN = r'(\w+://[\w\-\.]+(:(\d+)){0,1}/[\w]+)'

    @staticmethod
    def init(configFile):

        UrlUtils.SHORT_URL_TRANSLATOR_URL = getProperty(configFile, 'short-url-translator-url')

        UrlUtils.SHORT_URL_REFERER = getProperty(configFile, 'short-url-referer')
        UrlUtils.SHORT_URL_USER_AGENT = getProperty(configFile, 'short-url-user-agent')

        UrlUtils.SHORT_URL_SOURCE = getProperty(configFile, 'short-url-source')
        UrlUtils.SHORT_URL_CALLBACK = getProperty(configFile, 'short-url-callback')

    @staticmethod
    def toShortUrl(originalUrl):

        HEADERS = {
            'Referer': UrlUtils.SHORT_URL_REFERER,
            'User-Agent': UrlUtils.SHORT_URL_USER_AGENT
        }

        params = {'source': UrlUtils.SHORT_URL_SOURCE,
            'url_long': originalUrl,
            'callback': UrlUtils.SHORT_URL_CALLBACK}

        content = Network.getUrl(UrlUtils.SHORT_URL_TRANSLATOR_URL, params, HEADERS)

        start = content.find('(')
        end = content.rfind(')')

        if start < 0 or end < 0:
            return None

        obj = json.loads(content[start+1:end-1].decode('utf-8', 'ignore'))
        objs = obj.pop('urls')

        if objs is None or type(objs) is not list or 0 == len(objs):
            return None

        shortUrl = objs[0].pop('url_short')

        return shortUrl

    @staticmethod
    def toOriginalUrl(shortUrl):

        r = requests.get(shortUrl, allow_redirects=False)

        # HTTP 301: redirect(Permanently Moved)
        # HTTP 302: redirect(Temporarily Moved)
        if 301 == r.status_code or 302 == r.status_code:
            return r.headers['Location']

        return shortUrl

    @staticmethod
    def isShortUrl(url):
        return re.match(UrlUtils.HTTP_SHORT_URL_PATTERN, url) is not None

