#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import requests
import sys

from utils import getProperty

class NLP:

    NLP_URL = ''

    NLP_DATA_SCHEMA_KEYWORDS = ''
    NLP_API_KEYWORDS = ''

    NLP_DATA_SCHEME_MORPHOLOGY = ''
    NLP_API_MORPHOLOGY = ''

    NLP_ORIGIN = ''
    NLP_REFERER = ''
    NLP_USER_AGENT = ''

    @staticmethod
    def init(configFile):

        NLP.NLP_URL = getProperty(configFile, 'nlp-url')

        NLP.NLP_DATA_SCHEMA_KEYWORDS = getProperty(configFile, 'nlp-data-schema-keywords')
        NLP.NLP_API_KEYWORDS = getProperty(configFile, 'nlp-api-keywords')

        NLP.NLP_DATA_SCHEME_MORPHOLOGY = getProperty(configFile, 'nlp-data-scheme-morphology')
        NLP.NLP_API_MORPHOLOGY = getProperty(configFile, 'nlp-api-morphology')

        NLP.NLP_ORIGIN = getProperty(configFile, 'nlp-origin')
        NLP.NLP_REFERER = getProperty(configFile, 'nlp-referer')
        NLP.NLP_USER_AGENT = getProperty(configFile, 'nlp-user-agent')

    @staticmethod
    def invoke(data):

        NLP_HEADERS = {
            'Origin': NLP.NLP_ORIGIN,
            'Referer': NLP.NLP_REFERER,
            'User-Agent': NLP.NLP_USER_AGENT
        }

        NLP_COOKIES = {
            'pgv_pvi': '{}'.format(random.randint(1000000000, 9999999999)),
            'pgv_si': 's{}'.format(random.randint(1000000000, 9999999999))
        }

        r = requests.post(NLP.NLP_URL, data=data, cookies=NLP_COOKIES, headers=NLP_HEADERS)

        if 200 != r.status_code:
            print 'Error status: (', r.status_code, '):\n', r.text
            return None

        try:
            obj = json.loads(r.content.decode('utf-8', 'ignore'))
        except ValueError as e:
            print 'Wrong content: "', r.content, '"'
            return None

        if 'ret_code' not in obj.keys():
            print 'No code: (', obj, ')'
            return None

        errCode = int(obj.pop('ret_code'))

        if errCode is not 0:
            print 'Error code: (', errCode, ')'
            return None

        return obj

    @staticmethod
    def getKeywords(content):

        data = {
            'api': NLP.NLP_API_KEYWORDS,
            'body_data': NLP.NLP_DATA_SCHEMA_KEYWORDS.format(content)
        }

        obj = NLP.invoke(data)

        if obj is None:
            print 'No keyword for "', content, '"'
            return None

        return obj.pop('keywords')

    @staticmethod
    def getMorphology(content):

        data = {
            'api': NLP.NLP_API_MORPHOLOGY,
            'body_data': NLP.NLP_DATA_SCHEME_MORPHOLOGY.format(content)
        }

        obj = NLP.invoke(data)

        if obj is None:
            print 'No morphology for "', content, '"'
            return None

        return obj.pop('tokens')

