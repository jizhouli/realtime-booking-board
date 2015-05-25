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


class service_interface(service_base.service_base):
    
    _version = '2.0'
    _name = 'example_service'
    _file = ''
    _lines = []
    _zipvalue = {}
    _citydict = {}
    _spellcitydict = {}

    def init_thread_proc(self):
        self._servicelist = []
        self._serviceset = set()
        return {'result' : '0'}

    def reset_thread_proc(self):

        return {'result' : '0'} 

    def update_thread_proc(self):

        return {'result' : '0'} 

    def get_status(self):
        result = super(service_interface, self).get_status()
        result[self._name] = {
            'lines_count' : str(len(self._lines)),
            'file' : self._file,
        }
        return result

    def default_get(self, name):
        if name == 'register':
            info = {}
            info['host'] = web.ctx.environ['REMOTE_ADDR']
            info['port'] = web.ctx.environ['REMOTE_PORT']
            if info['host'] + '_' + info['port'] not in self._serviceset:
                self._servicelist.append(info)
                self._serviceset.add(info['host'] + '_' + info['port'])
            return {'result' : '0'} 
        if name == 'getinstance':
            result = {}
            result['data'] = self._servicelist
            result['result'] = '0'
            return result

    def default_post(self, name):

        return {'result' : '0'}
        
_instance = None
def get_instance():
    global _instance
    if _instance is None:
        _instance = service_interface()
    return _instance

if __name__ == "__main__": 
    print "service_interface done"
