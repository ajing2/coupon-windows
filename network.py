import httplib  
import os
import random
import requests
import socket
import time

from utils import chmod

class Network:

    _instance = None

    def __init__(self):
        self.isLocal = True

    @staticmethod
    def setIsLocal(isLocal):

        if Network._instance is None:
            Network._instance = Network()

        Network._instance.isLocal = isLocal

    @staticmethod
    def get(url, params=None, **kwargs):

        try:
            return requests.get(url, params=params, **kwargs)
        except Exception as e:
            print 'Error to get', url, ':', e

        return None

    @staticmethod
    def post(url, data=None, json=None, **kwargs):

        try:
            return requests.post(url, data=data, json=json, **kwargs)
        except Exception as e:
            print 'Error to post', url, ':', e

        return None

    @staticmethod
    def getUrl(url, params=None, headers=None):

        if Network._instance is None:
            Network._instance = Network()

        content = Network._instance.getUrlImpl(url, params, headers)

        # Sleep for a while
        if content is not None:
            time.sleep(random.random())

        return content

    def getUrlImpl(self, url, params, headers):

        r = Network.get(url, params=params, headers=headers)

        if r is None:
            return ''

        # TODO: add other judgement for http response
        return r.text

    @staticmethod
    def saveGetUrl(pathname, url, force=False):

        if Network._instance is None:
            Network._instance = Network()

        ret = Network._instance.saveGetUrlImpl(pathname, url, force)

        # Sleep for a while
        if ret is 0:
            print 'Updated', pathname
            time.sleep(random.random())

        return ret

    def saveGetUrlImpl(self, pathname, url, force=False):

        if not force and self.isLocal and os.path.exists(pathname):
            return 1

        r = Network.get(url)
        if r is None:
            return -1

        # TODO: add other judgement for http response

        with open(pathname, 'wb') as fp:
            fp.write(r.content)

        chmod(pathname)

        return 0
 
    @staticmethod
    def saveHttpData(pathname, url, host=None, force=False):

        if Network._instance is None:
            Network._instance = Network()

        ret = Network._instance.saveHttpDataImpl(pathname, url, host, force)

        # Sleep for a while
        if ret is 0:
            print 'Updated', pathname
            time.sleep(random.random())

        return ret

    def saveHttpDataImpl(self, pathname, url, host, force=False):

        if not force and self.isLocal and os.path.exists(pathname):
            return 1

        if None == host:
            start = url.find('//') + 2
            end = url[start:].find('/')

            host = url[start:start+end]
            url = url[start+end:]

        for i in range(0, 3):
            conn = httplib.HTTPConnection(host, timeout=10)  

            try:
                conn.request("GET", url)
                res = conn.getresponse()

                if 200 != res.status:
                    print res.status, res.reason
                    continue

                data = res.read()

            except Exception:
                print 'Timeout, try it again. NO. ', i+1

                # Sleep a while
                time.sleep(30 * i)
                continue

            finally:
                conn.close()

            fp = open(pathname, 'w')
            fp.write(data)
            fp.close()

            chmod(pathname)

            return 0

        return -1

