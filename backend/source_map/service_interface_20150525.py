#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: shichao
# Date: 2012/10/22

import threading
import os
import sys
import pickle
import web
import re
import time
import ujson as json
import service_base
import traceback
import urllib2

import MySQLdb
import types
import string
from datetime import datetime, timedelta
import httplib
import copy
import pickle

import logging
import logging.handlers

LSAT_ONLINE_DATA = 'onlinehotelid.last'

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASIC_PATH = os.path.realpath(os.path.join(BASE_PATH, 'reset'))
UPDATE_PATH = os.path.realpath(os.path.join(BASE_PATH, 'update'))
DUMP_PATH = os.path.realpath(os.path.join(BASE_PATH, 'dump'))
DUMP_FILE = 'dump.data'

def http_access(host, url, port=80, method='GET', body=''):
    try:
        jbody = json.dumps(body) if body else None
        c = httplib.HTTPConnection(host, port)
        c.request(method, url, jbody)
        r = c.getresponse()
        if r.status != 200:
            return {'result' : str(r.status), 'reason' : 'http return %d' % r.status}
        b = r.read()
        c.close()
        return json.loads(b)
    except Exception, e:
        return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}

def set_db_conf():
    db_conf = {}

    host = 'service.kuxun.cn'
    url = '/hotel_env/?node="db"'
    resp = http_access(host, url)
    if resp['result'] == '0':
        db_node = 'db_edit_offline_query'
        d = resp['data']['db'][db_node]
        db_conf['host'] = d['host']
        db_conf['user'] = d['r']['user']
        db_conf['passwd'] = d['r']['passwd']
        db_conf['db'] = d['name']
        db_conf['port'] = d['port']
    return db_conf

class _UniLogger(logging.getLoggerClass()):
    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls("")
        return cls._instance

unilogger = _UniLogger.instance()

def rotating_sample(logname):
    rotating_file_handler = logging.handlers.RotatingFileHandler(logname, "a", 134217728, 7)
    fmt = logging.Formatter("%(asctime)s %(levelname)-5s %(message)s", "%x %X")
    rotating_file_handler.setFormatter(fmt)
    unilogger.addHandler(rotating_file_handler)

def console_sample():
    console = logging.StreamHandler()
    fmt = logging.Formatter("%(filename)s(%(lineno)d): [%(levelname)s] %(message)s", "%x %X")
    console.setFormatter(fmt)
    unilogger.addHandler(console)

class dbfunc(object):
    def __init__(self, host, user, password, db, port=3306, charset='utf8'):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.port = port

        self.connect()

    def connect(self):
        ret = True
        try:
            self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.db, charset=self.charset, port=self.port)
            self.cursor = self.conn.cursor()
            self.cursor.execute('SET NAMES %s' % self.charset)
            self.cursor.execute('SET CHARACTER_SET_CLIENT=%s' % self.charset)
            self.cursor.execute('SET CHARACTER_SET_RESULTS=%s' % self.charset)
            self.conn.commit()
            #print 'mysql connection succeed'
            unilogger.info('mysql_conection_succeed')
        except MySQLdb.Error, e:
            #print >>sys.stderr, 'mysql conection fail'
            unilogger.info('mysql_conection_fail')
            ret = False
        
        return ret

    def execute(self, sql, args=None):
        if type(sql) is not types.UnicodeType:
            sql = sql.decode(self.charset, 'ignore')
        try:
            ret = []
            self.cursor.execute(sql)
            self.conn.commit()
            #print 'execute sql right'
            unilogger.info('execute_sql_right %s', sql)
        except Exception, e:
            #print 'execute sql wrong'
            unilogger.info('execute_sql_wrong %s', sql)

    def get_all_dict(self, sql, args=None):
        ret = []
        self.execute(sql, args)
        rs = self.cursor.fetchall()
        fields = [i[0] for i in self.cursor.description]
        for row in rs:
            j = 0
            temp = {}
            for item in row:
                temp[fields[j]] = item
                j += 1
            if temp:
                ret.append(temp)
        return ret

    def close(self):
        self.conn.close()
        self.conn = None

def post_service_data(host, port, name, content):
    url = 'http://%s:%s/%s?reserved="1"' % (host, port, name)
    jdata = json.dumps(content)
    req = urllib2.Request(url, jdata)
    response = urllib2.urlopen(req)
    return response.read()

def get_active_service(host, port, name):
    url = 'http://%s:%s/%s?reserved="1"' % (host, port, name)
    ret = urllib2.urlopen(url)
    return ret.read()

class service_interface(service_base.service_base):
    
    _version = '2.0'
    _name = 'example_service'
    _file = ''
    _lines = []
    _zipvalue = {}
    _citydict = {}   # this is city each second
    _spellcitydict = {}
    _totalservicelist = []

    def get_city_service(self):
        cityspelldict = {}
        db_conf = set_db_conf()
        handler = dbfunc(db_conf['host'], db_conf['user'], db_conf['passwd'], db_conf['db'], db_conf['port'])
        query = "select word, uniq_spell, type_id from trans_hotel_spell where type in('city', 'county')"
        ret =  handler.get_all_dict(query)
        for i in range(0, len(ret)):
            self._spellcitydict[str(ret[i]['uniq_spell'])] = {'chinese': ret[i]['word'], 'city_id': ret[i]['type_id']}
            cityspelldict[str(ret[i]['type_id'])] = str(ret[i]['uniq_spell'])

        count = 1
        query = "select b_latitude, b_longitude, city_id from trans_hotel_info where b_latitude<>0 and b_longitude<>0 group by city_id"
        ret =  handler.get_all_dict(query)
        for i in range(0, len(ret)):
            count += 1
            if cityspelldict.get(str(ret[i]['city_id']), ' ') != ' ':
                if self._spellcitydict.get(cityspelldict[str(ret[i]['city_id'])], ' ') != ' ':
                    self._spellcitydict[cityspelldict[str(ret[i]['city_id'])]]['latitude'] = str(ret[i]['b_latitude'])
                    self._spellcitydict[cityspelldict[str(ret[i]['city_id'])]]['longitude'] = str(ret[i]['b_longitude'])
        print self._spellcitydict, 'CCCCCCCCCCCC'

        handler.close()

    def init_thread_proc(self):
        print len(sys.argv), '@@@@@@@@@@@@@@@@@@', sys.argv[0], sys.argv[1]
        try:
            if os.path.isfile(DUMP_PATH + '/' + DUMP_FILE):
                fpdump = open(DUMP_PATH + '/' + DUMP_FILE)
                totaldict = pickle.load(fpdump)
                fpdump.close()
                self._spellcitydict = totaldict['spellcitydict']
                self._citydict = totaldict['citydict']
            else:
                self.get_city_service()
        except:
            pass

        print '###########################################'

        #get_active_service('192.168.0.24', '8030', 'register')
        post_service_data('192.168.0.24', '8030', 'register', sys.argv)
        print 'aaaaaaaaaaaaaaa'
        rawretdata = get_active_service('192.168.0.24', '8030', 'getinstance')
        retdata = json.loads(rawretdata)
        self._totalservicelist = retdata['data']
        print retdata, 'ccccccccccccc', retdata['data']
        if len(retdata['data']) != 1:
            print 'DDDDDDDDDDDDDD'
            tempnode = retdata['data'][0]
            print tempnode['host'], tempnode['port'], 'othersget', 'fFFFFFFFFFFF'
            rawtotaldict = get_active_service(tempnode['host'], tempnode['port'], 'othersget')
            print rawtotaldict, 'GGGGGGGGGGG'
            totaldict = json.loads(rawtotaldict)['data']
            self._citydict = totaldict['citydict']
            self._spellcitydict = totaldict['spellcitydict']

        print self._spellcitydict, 'AAAAAAAAAAA'
        print self._citydict, 'BBBBBBBBBB'

        self.set_auto_update(1)

        return {'result' : '0'}

    def reset_thread_proc(self):

        return {'result' : '0'} 

    def update_thread_proc(self):
        print 'this is update  ******************************************************8888888888888888888888'

        a = time.localtime(time.time())
        hour, minute, second = a[3], a[4], a[5]
        if hour-1 < 0:
            hour = 23
        else:
            hour = hour-1
        secondset = set()
        for each in self._citydict:
            secondset.add(each)
        for each in secondset:
            if int(each[:2]) < hour and int(each[:2]) != 0:
                try:
                    del self._citydict[each]
                except:
                    pass

        totaldict = {}
        totaldict['citydict'] = self._citydict
        totaldict['spellcitydict'] = self._spellcitydict
        fpdump = file(DUMP_PATH + '/' + DUMP_FILE, 'w')
        pickle.dump(totaldict, fpdump)
        fpdump.close()

        return {'result' : '0'} 

    def get_status(self):
        result = super(service_interface, self).get_status()
        result[self._name] = {
            'lines_count' : str(len(self._lines)),
            'file' : self._file,
        }
        return result

    def get_citydict(self, querydata):
        result = {}
        forretcity = {}
        a = time.localtime(time.time())
        hour, minute, second = a[3], a[4], a[5]
        currentsecond = '%02d:%02d:%02d' % (hour, minute, second)
        tempdata =  querydata['data'][0]['value'][0]
        #print tempdata[0], tempdata[1], 'bbbbbbbbbbb'
        if len(tempdata) == 1:
            tempdata.append(currentsecond)
        else:
            if currentsecond > tempdata[1] or (tempdata[1] >= '00:00:00' and currentsecond > '23:00:00'):
                currentsecond = tempdata[1]

        retcityset = set()
        datas = tempdata[1].split(':')
        hour, minute, second = int(datas[0]), int(datas[1]), int(datas[2])
        while True:
            if len(retcityset) >= 100:
                break
            if second-1 <  0 :
                second = 59
                if minute-1 < 0:
                    minute = 59
                    hour = hour-1
                else:
                    minute = minute-1
            else:
                second = second - 1
            one_second_before = '%02d:%02d:%02d' % (hour, minute, second)
            if one_second_before != tempdata[0]:
                try:
                    for each in self._citydict[one_second_before]:
                        retcityset.add(each)
                        if forretcity.get(each, ' ') == ' ':
                            forretcity[each] = self._citydict[one_second_before][each]
                        else:
                            forretcity[each] += self._citydict[one_second_before][each]
                        if len(retcityset) >= 100:
                            break
                except:
                    pass
            else:
                break

        realdata = {}
        for each in forretcity:
            try:
                info = {}
                info['city_name'] = self._spellcitydict[each]['chinese']
                info['number'] = forretcity[each]
                info['latitude'] = self._spellcitydict[each]['latitude']
                info['longitude'] = self._spellcitydict[each]['longitude']
                realdata[each] = info
            except:
                pass

        result['data'] = realdata
        result['currenttime'] = currentsecond
        result['citynumber'] = len(retcityset)
        result['result'] = 0
        return result

    def default_get(self, name):
        print name, 'EEEEEEEEEEEEEEEEEEEEEE'
        if name == 'othersget':
            print 'JJJJJJJJJJJJJJJJ'
            totaldict = {}
            #info = {}
            #info['host'] = web.ctx.environ['REMOTE_ADDR']
            #info['port'] = web.ctx.environ['REMOTE_PORT']
            #self._totalservicelist.append(info)
            totaldict['citydict'] = self._citydict
            totaldict['spellcitydict'] = self._spellcitydict
            #totaldict['totalservicelist'] = self._totalservicelist
            result = {}
            result['data'] = totaldict
            result['result'] = '0'
            return result
        if name == 'frontget':
            querydata = self.query_to_value()
            return self.get_citydict(querydata)

    def default_post(self, name):
        # default name is 'timedata'
        #result = {}
        print 'name:', name
        print web.ctx.query, '4444444444'
        print web.data(), '3eeeeeeeeeee'
        querydata = self.query_to_value()
        postdata = self.json_loads(web.data())
        print querydata, postdata, '111111111111'

        a = time.localtime(time.time())
        hour, minute, second = a[3], a[4], a[5]
        currentsecond = '%02d:%02d:%02d' % (hour, minute, second)
        #currentsecond = 'test'
        if self._citydict.get(currentsecond, ' ') == ' ':
            self._citydict[currentsecond] = {}
        for each in postdata:
            if self._citydict[currentsecond].get(each, ' ') == ' ':
                self._citydict[currentsecond][each] = postdata[each]
            else:
                self._citydict[currentsecond][each] += postdata[each] 
        print self._citydict, '5555555555555'
        #if name != 'otherspost':
        #    for each in self._totalservicelist:
        #        post_service_data(each['host'], each['port'], 'otherspost', web.data())

        return {'result' : '0'}
        
_instance = None
def get_instance():
    global _instance
    if _instance is None:
        _instance = service_interface()
    return _instance

if __name__ == "__main__": 
    print "service_interface done"
