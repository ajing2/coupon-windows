import dataset
import sqlalchemy

import MySQLdb

from urllib import quote_plus as urlquote
from utils import getProperty, AutoReleaseThread

def toDbText(src):
    if None == src or 0 == len(src): return ''
    return src.replace('\'', '').replace('"', '')

class Database(AutoReleaseThread):

    def __init__(self, configFile, dbName):

        AutoReleaseThread.__init__(self)

        self.host = getProperty(configFile, 'mysql-host')
        self.username = getProperty(configFile, 'mysql-user')
        self.password = getProperty(configFile, 'mysql-password')

        self.enabled = False

        enabled = getProperty(configFile, 'db-enabled')

        if None != enabled:
            enabled = enabled.upper()
            if 'Y' == enabled or 'YES' == enabled:
                self.enabled = True

        self.dbName = dbName
        self.db = None
        self.tableDict = None

        if self.enabled:
            self.start()

    def onInitialized(self):

        if self.db is not None:
            return

        # XXX: Higher version would NOT raise an exception if database doesn't exist
        if self.connectDb():
            return

        self.createDb()
        self.connectDb()

    def onReleased(self):

        if not self.enabled:
            return

        if self.db is None:
            return

        if self.tableDict is not None:
            self.tableDict.clear()
            self.tableDict = None

        self.db.commit()
        self.db = None

    def createDb(self):

        conn = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password)

        try:
            print 'Creating', self.dbName, 'in', self.host
            conn.cursor().execute('CREATE DATABASE IF NOT EXISTS {}'.format(self.dbName))
            print 'Created', self.dbName, 'in', self.host
        except MySQLdb.OperationalError as e:
            print 'Unable to create DB', self.dbName, 'in', self.host
        finally:
            conn.commit()
            conn.close()

    def connectDb(self):

        try:
            url = 'mysql://{}:{}@{}/{}?charset=utf8'.format(self.username,
                urlquote(self.password), self.host, self.dbName)

            print 'Connecting', self.dbName, 'in', self.host
            self.db = dataset.connect(url)

            # XXX: Workaround to post an error because current design of dataset
            executable = self.db.executable
            print 'Connected', self.dbName, 'in', self.host
            return True

        except sqlalchemy.exc.OperationalError as e:
            return False

    def getTable(self, tableName):

        if not self.enabled: return True

        self.initialize()

        if self.tableDict is not None and self.tableDict.has_key(tableName):
            return self.tableDict[tableName]

        if self.tableDict is None:
            self.tableDict = dict()

        # XXX: get_table will auto create if not exists however load_table won't.
        table = self.db.get_table(tableName)

        self.tableDict[tableName] = table

        return table

    def findOne(self, tableName, *args, **kwargs):

        if not self.enabled: return False

        return self.getTable(tableName).find_one(*args, **kwargs)

    def insert(self, tableName, recordDict, alterKeys=None):

        if not self.enabled: return 0

        try:
            recordId = self.getTable(tableName).insert(recordDict)

        except Exception as e:
            # XXX: Unable to insert a record
            print 'DATABASE ERROR:\n', e
            recordId = 0L

        # TODO: not a good solution
        if alterKeys is not None and (0 == recordId or 1 == recordId):

            data = dict()

            for key in alterKeys:
                data[key] = recordDict[key]

            self.alterColumn(tableName, data)

            if 0 == recordId:
                recordId = self.getTable(tableName).insert(recordDict)
            else: # 1L
                data['id'] = recordId
                self.update(tableName, data, ['id'])

        return recordId

    def update(self, tableName, recordDict, keys):

        if not self.enabled: return True

        self.getTable(tableName).update(recordDict, keys)

    def query(self, sql):

        if not self.enabled: return None

        self.initialize()

        try:
            return self.db.query(sql)
        except sqlalchemy.exc.ProgrammingError as e:
            print 'DATABASE ERROR (', e, '):', sql

        return None

    def alterColumn(self, tableName, recordDict):

        def generateSql(tableName, columnName, columnValue):

            if columnValue is None:
                return None
            elif isinstance(columnValue, unicode):
                return ("ALTER TABLE `{0}` "
                        "CHANGE `{1}` `{1}` TEXT CHARACTER "
                        "SET utf8 COLLATE utf8_general_ci NULL "
                        "DEFAULT NULL;").format(tableName, columnName)
            elif isinstance(columnValue, int):
                return ("ALTER TABLE `{0}` "
                        "CHANGE `{1}` `{1}` BIGINT NULL "
                        "DEFAULT NULL;").format(tableName, columnName)
            elif isinstance(columnValue, float):
                return ("ALTER TABLE `{0}` "
                        "CHANGE `{1}` `{1}` DOUBLE NULL "
                        "DEFAULT NULL;").format(tableName, columnName)
            elif isinstance(columnValue, long):
                # Do nothing
                return None
            else:
                raise TypeError('No implement of {} and type {}'.format(columnName,
                    type(columnValue)))

        for (k, v) in recordDict.items():
            sql = generateSql(tableName, k, v)
            if sql is not None:
                self.query(sql)

