#!/usr/bin/env python
# -*- coding:utf-8 -*-

from utils import getProperty

class Validation:

    BAD_COMMENTS = None
    BAD_COMMENTS_MIN_RATIO = 0.3
    BAD_COMMENTS_MIN_LEN = 200 # If its length is much long, it's likely to be a bad one.

    @staticmethod
    def init(configFile):
        Validation.BAD_COMMENTS = getProperty(configFile, 'bad-comments')

    @staticmethod
    def isCommentBad(comment):

        if comment is None:
            return True

        size = len(comment)

        if 0 == size or size >= Validation.BAD_COMMENTS_MIN_LEN:
            return True

        num = 0
        for char in comment:
            if char in Validation.BAD_COMMENTS:
                num += 1

        ratio = float(num) / float(size)
        return (ratio >= Validation.BAD_COMMENTS_MIN_RATIO)

