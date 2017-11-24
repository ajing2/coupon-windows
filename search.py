#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

from utils import getMatchString

class SearchingKeyRegex:

    _instance = None

    def __init__(self):

        self.rules = list()

        with open('templates/search.json') as fp:

            obj = json.loads(fp.read())
            if obj is None:
                return None

            for rule in obj['rule-list']:
                self.rules.append(r'{}'.format(rule['rule']))

    def parseImpl(self, content):

        for i in range(1):

            start = content.find('#')
            if start < 0:
                break

            end = content.rfind('#')
            if end is start:
                break

            return content[start:end+1]

        for rule in self.rules:
            value = getMatchString(content, rule)

            if value is not None:

                value = value.strip()
                if len(value) > 0:
                    return '#{}#'.format(value)

        return None

    @staticmethod
    def parse(content):

        if SearchingKeyRegex._instance is None:
            SearchingKeyRegex._instance = SearchingKeyRegex()

        return SearchingKeyRegex._instance.parseImpl(content)

