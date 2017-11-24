# -*- coding:utf-8 -*-

import codecs
import json
import os
import random
import re
import requests
import time

from imgkit import ImageKit
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from utils import chmod, getMatchString, getProperty, inputElement, randomSleep, reprDict, OutputPath

class CPS:

    def __init__(self):
        pass

    def login(self):
        pass

    def getSkuId(self):
        pass

class QWD:

    def __init__(self, configFile):

        self.configFile = configFile

        self.loginMethod = int(getProperty(self.configFile, 'cps-qwd-login-method'))

        self.ploginUrl = getProperty(self.configFile, 'cps-qwd-plogin-url')
        self.ploginSeccessfulUrl = getProperty(self.configFile, 'cps-qwd-plogin-seccessful-url')

        self.appid = getProperty(self.configFile, 'cps-qwd-appid')
        self.ctype = getProperty(self.configFile, 'cps-qwd-ctype')
        self.ie = getProperty(self.configFile, 'cps-qwd-ie')
        self.p = getProperty(self.configFile, 'cps-qwd-p')
        self.qwd_chn = getProperty(self.configFile, 'cps-qwd-qwd_chn')
        self.qwd_schn = getProperty(self.configFile, 'cps-qwd-qwd_schn')
        self.login_mode = getProperty(self.configFile, 'cps-qwd-login_mode')

        self.pageindex = getProperty(self.configFile, 'cps-qwd-pageindex')
        self.pagesize = getProperty(self.configFile, 'cps-qwd-pagesize')
        self.uniquespu = getProperty(self.configFile, 'cps-qwd-uniquespu')
        self.storestatus = getProperty(self.configFile, 'cps-qwd-storestatus')
        self.comsrate = getProperty(self.configFile, 'cps-qwd-comsrate')

        self.sortBy = getProperty(self.configFile, 'cps-qwd-sortby').split(';')
        self.order = getProperty(self.configFile, 'cps-qwd-order').split(';')

        self.coupon = getProperty(self.configFile, 'cps-qwd-coupon')
        self.pwprice = getProperty(self.configFile, 'cps-qwd-pwprice')
        self.delivery = getProperty(self.configFile, 'cps-qwd-delivery')

        self.uuid = getProperty(self.configFile, 'cps-qwd-uuid')

        self.pin = getProperty(self.configFile, 'cps-qwd-pin')
        self.password = getProperty(self.configFile, 'cps-qwd-password')
        self.tgt = getProperty(self.configFile, 'cps-qwd-tgt')

        self.shareUrl = getProperty(self.configFile, 'cps-qwd-share-url')
        self.searchItemUrl = getProperty(self.configFile, 'cps-qwd-search-item-url')

        self.userAgent = getProperty(self.configFile, 'cps-qwd-http-user-agent')

        self.reset()

    def reset(self):

        self.apptoken = None
        self.pinType = None
        self.jxjpin = None

        #XXX: Can NOT use session to store cookie because these fields are not
        #     valid http cookie.
        self.cookies = dict()

        self.pCookies = None

    def login(self):

        if self.apptoken is not None:
            return True

        # Url
        url = getProperty(self.configFile, 'cps-qwd-login-url')

        # Data
        data = {'appid': self.appid,
                'ctype': self.ctype,
                'ie': self.ie,
                'p': self.p,
                'pin': self.pin,
                'tgt': self.tgt,
                'uuid': self.uuid}

        # Request
        r = requests.post(url, data=data)
        response = r.content

        obj = json.loads(response.decode('utf-8', 'ignore'))

        # Login status
        errCode = int(obj.pop('errCode'))

        if errCode is not 0:
            print 'Failed to login to', url, ':\n', response
            return False

        print('Logined to qwd.jd.com')

        obj = obj.pop('loginInfo')

        self.apptoken = obj.pop('apptoken')
        self.pinType = obj.pop('pinType')
        self.jxjpin = obj.pop('jxjpin')

        self.cookies = {'app_id': self.appid,
                'apptoken': self.apptoken,
                'client_type': self.ctype,
                'jxjpin': self.jxjpin,
                'pinType': self.pinType,
                'tgt': self.tgt,
                'qwd_chn': self.qwd_chn,
                'qwd_schn': self.qwd_schn,
                'login_mode': self.login_mode}

        return True

    @staticmethod
    def isValidShareUrl(url):

        pattern = r'(https://union-click\.jd\.com/jdc\?d=\w+)'

        return re.match(pattern, url) is not None

    def getShareUrl(self, skuid):

        if self.loginMethod is 1:
            self.plogin()
            cookies = self.pCookies
        else:
            self.login()
            cookies = self.cookies

        url = self.shareUrl.format(skuid)

        headers = {'User-Agent': self.userAgent}

        try:
            r = requests.get(url, cookies=cookies, headers=headers)
        except Exception as e: 
            print 'Unable to get sharing URL for "', skuid, '" with an error:\n', e
            return None

        if 200 != r.status_code:
            print 'Unable to get sharing URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        content = r.content.replace('\n', '')
        data = getMatchString(content, r'itemshare\((.*?)\)')

        obj = json.loads(data.decode('utf-8', 'ignore'))
        retCode = int(obj.pop('retCode'))

        if retCode is not 0:
            print 'Unable to get sharing URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text

            # XXX: Reset but let this message failed because of less complicated logistic. It will re-login
            #      when call the function again.
            self.reset()

            return None

        return obj.pop('skuurl')

    def getSkuId(self, url):

        headers = {'User-Agent': self.userAgent}
        r = requests.get(url, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get long URL for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        url = getMatchString(r.content, r"hrl='(.*?)'")
        #print 'Long url:', url

        headers = {'User-Agent': self.userAgent}
        r = requests.get(url, headers=headers)

        if 200 != r.status_code:
            print 'Unable to get information page for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return None

        data = getMatchString(r.content, r'window._itemOnly = (.*?);')
        #print data

        obj = json.loads(data.decode('utf-8', 'ignore'))
        obj = obj.pop('item')

        skuId = obj.pop('areaSkuId')

        return skuId

    # cut-type: 0, none; 1, coupon; 2, discount
    # prices: lowPrice, highPrice
    # sort by: 0, none; 1, wechat_price; 2, total_qtty; 3, good_comments
    # order: 0, asc; 1, desc;
    # delivery: 0, none; 1, jd delivery
    def search(self, key, cutType=0, price=None, sortByType=0, orderType=0, deliveryType=0):

        def formatPrice(low, high):
            if high is 0: 
                return '0-00'
            return '{}-{}'.format(low, high)

        payload = {'g_tk': random.randint(1000000000, 9999999999),
                'pageindex': self.pageindex,
                'pagesize': self.pagesize,
                'uniquespu': self.uniquespu,
                'storestatus': self.storestatus,
                'ie': self.ie,
                '_': int(time.time() * 1000)}

        # Commission Rate
        commissionRateData = {'comsrate': self.comsrate}
        payload.update(commissionRateData)

        # Key
        payload.update({'key': key, 'text': key})

        # Cut type
        if cutType is 1:
            payload.update({'coupon': self.coupon})
        elif cutType is 2:
            payload.update({'pwprice': self.pwprice})

        # Delivery
        if deliveryType is 1:
            payload.update({'delivery': self.delivery})

        # Price
        if price is not None and isinstance(price, tuple):
            payload.update({'wprice': formatPrice(price[0], price[1])})

        # Sort by
        if sortByType is not 0:

            sortByType -= 1

            payload.update({'sortby': self.sortBy[sortByType]})
            # Order
            payload.update({'order': self.order[orderType]})

        # Headers
        headers = {'User-Agent': self.userAgent}

        print 'Searching remotely with:', payload

        try:
            r = requests.get(self.searchItemUrl, params=payload, headers=headers)
        except Exception as e: 
            print 'Unable to search "', key, '" with price', price, ' because of an error:\n', e
            return None

        if 200 != r.status_code:
            print 'Unable to search "', key, '" with price', price, ' because of an error (', r.status_code, '):\n', r.text
            return None

        obj = json.loads(r.content.decode('utf-8', 'ignore'))
        errCode = int(obj.pop('errCode'))

        if errCode is not 0:
            print 'Wrong error code:', errCode
            return None

        return obj.pop('sku')

    def getImageUrl(self, skuid):

        skus = self.search(skuid)

        if skus is None:
            print 'No sku'
            return None

        for sku in skus:
            if sku['skuid'] == str(skuid):
                return sku['skuimgurl']

        return None

    def saveImage(self, path, skuid):

        url = self.getImageUrl(skuid)
        if url is None:
            return False

        r = requests.get(url)

        if 200 != r.status_code:
            print 'Unable to get image data for "', skuid, '" with an error (', r.status_code, '):\n', r.text
            return False

        with codecs.open(path, 'wb') as fp:
            fp.write(r.content)

        chmod(path)

        return True

    def getBrowserError(self, browser):

        wait = WebDriverWait(browser, 3)
      
        try:
            page_loaded = wait.until_not(lambda browser: browser.current_url == self.ploginUrl)
            return None
        except Exception as e:
            pass

        noticeElement = browser.find_element_by_xpath('//div[@class="notice"]')
        return browser.execute_script("return arguments[0].innerHTML", noticeElement)

    def plogin(self):

        def isValidAuthCode(code):

            if code is None or len(code) != 4:
                return False

            for c in code:

                if c.isdigit():
                    continue

                if c.isalpha():
                    continue

                # Wrong word
                return False

            return True

        if self.pCookies is not None:
            return True

        # https://github.com/mozilla/geckodriver/releases
        # browser = webdriver.Firefox()

        # https://chromedriver.storage.googleapis.com/index.html
        browser = webdriver.Chrome()

        try:
            # Plogin
            browser.get(self.ploginUrl)

            # Login by username and password

            # Username and password
            randomSleep(1, 2)
            inputElement(browser.find_element_by_id('username'), self.pin)

            randomSleep(1, 2)
            inputElement(browser.find_element_by_id('password'), self.password)

            # Submit
            buttonElement = browser.find_element_by_id('loginBtn')

            # Code
            codeElement = browser.find_element_by_id('code')
            imageElement = browser.find_element_by_id('imgCode')

            times = 0

            if codeElement.is_displayed():

                while codeElement.is_displayed() and times < 50:

                    times += 1

                    # Image to text
                    path = OutputPath.getAuthPath(self.pin)

                    ImageKit.saveCapture(browser, imageElement, path)

                    code = ImageKit.getText(path)

                    codeElement.send_keys(code)

                    if not isValidAuthCode(code):

                        # Refresh auth code
                        randomSleep(0.5, 1)
                        imageElement.click()

                        # Wait for updating auth code 
                        randomSleep(1, 2)
                        codeElement.clear()

                        continue

                    # Submit
                    randomSleep(1, 2)
                    buttonElement.click()

                    error = self.getBrowserError(browser)

                    if error is None:
                        print 'Succeed after', times, 'tries.'
                        break

                    if u'验证码' not in error:
                        raise Exception('Unable to login for "{}": {}'.format(self.pin, error))

                    randomSleep(1, 2)
                    codeElement.clear()
                    randomSleep(1, 2)

                else:
                    raise Exception('Unable to login for "{}"'.format(self.pin))

            else:
                # Submit
                randomSleep(1, 2)
                buttonElement.click()

                wait = WebDriverWait(browser, 3)
              
                error = self.getBrowserError(browser)

                if error is not None:
                    raise Exception('Unable to login for "{}": {}'.format(self.pin, error))

            print 'Loginned for', self.pin

            # Redirect to wqs
            qwsUrl = getProperty(self.configFile, 'cps-qwd-wqs-url')

            browser.get(qwsUrl)
            time.sleep(10)

            # Save as type of cookie for requests
            self.pCookies = dict()
            for cookie in browser.get_cookies():

                k = cookie['name']
                v = cookie['value']

                self.pCookies[k] = v

        except Exception as e:
            print e
        finally:
            browser.quit()

