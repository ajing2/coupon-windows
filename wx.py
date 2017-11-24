# -*- coding:utf-8 -*-

import random
import itchat
import time

from schedule import Schedule
from search import SearchingKeyRegex
from special import Searcher
from utils import getProperty, randomSleep, reprDict

class WX(Schedule):

    def __init__(self, configFile):

        Schedule.__init__(self, configFile)

        self.searcher = Searcher(configFile)

        self.configFile = configFile

    def login(self, exitCallback, uuid=None):

        def isLoginned(uuid):

            for count in range(10):

                status = int(itchat.check_login(uuid))

                if status is 200:
                    return True

                if status is 201:
                    print 'Wait for confirm in mobile #', count
                    randomSleep(1, 2)
                    continue

                print 'Error status:', status
                return False

            return False

        if uuid is None:

            statusFile = getProperty(self.configFile, 'wechat-status-file')
            itchat.auto_login(hotReload=True, statusStorageDir=statusFile)

        else:

            if not isLoginned(uuid):
                raise Exception('Failed to login with {}'.format(uuid))

            userInfo = itchat.web_init()

            itchat.show_mobile_login()
            itchat.get_friends(True)

            itchat.start_receiving(exitCallback)

        self.me = itchat.search_friends()

        print self.me['NickName'], 'is working'

        self.watchFriends = list()
        names = getProperty(self.configFile, 'wechat-watch-friends').split(';')
        for name in names:
            friends = itchat.search_friends(name=name) 
            self.watchFriends.extend(friends)

        self.watchGroups = list()
        names = getProperty(self.configFile, 'wechat-watch-groups').split(';')
        for name in names:
            groups = itchat.search_chatrooms(name=name)
            self.watchGroups.extend(groups)

        self.searchReplyPlate = getProperty(self.configFile, 'search-reply-plate')

        itchat.run(blockThread=False) # Run in a new thread

        self.run()

    @staticmethod
    def sendTo(obj, plate=None, image=None):

        print '================================================================'
        print 'Send a message to', obj['NickName']

        if plate is not None:

            interval = random.random() * 10
            time.sleep(interval)

            ret = obj.send(plate)

            print 'Result of text message:', ret['BaseResponse']['ErrMsg']
            print '----------------------------------------------------------------'
            print plate
            print '----------------------------------------------------------------'

        if image is not None:

            interval = random.random() * 10
            time.sleep(interval)

            ret = obj.send_image(image)
            print 'Result of', image, ':', ret['BaseResponse']['ErrMsg']

            print '================================================================'

    def text(self, msg):

        for friend in self.watchFriends:
            if msg['FromUserName'] == friend['UserName']:
                break
        else:
            return

        print '================================================================'
        print msg['User']['NickName'], 'sends a message:'
        print '----------------------------------------------------------------'
        print msg['Content']
        print '================================================================'

        self.search(friend, msg['Content'])
    def textGroup(self, msg):

        for friend in self.watchGroups:
            if msg['FromUserName'] == friend['UserName']:
                break
        else:
            return

        print '================================================================'
        print msg['User']['NickName'], 'sends a message:'
        print '----------------------------------------------------------------'
        print msg['Content']
        print '================================================================'

        self.search(friend, msg['Content'])

    def send(self, plate, image):

        for friend in self.watchFriends:
            WX.sendTo(friend, plate, image)

    def search(self, friend, content):

        content = SearchingKeyRegex.parse(content)

        if content is None:
            return

        print 'Searching', content

        WX.sendTo(friend, self.searchReplyPlate.format(content.replace('#', ' ')))

        if not self.searcher.search(content):
            return

        WX.sendTo(friend, self.searcher.plate, self.searcher.image)

