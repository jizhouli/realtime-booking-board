#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Yan Antao
# Date: 2012/10/11

import os
import time
import datetime
import threading
import string
import web
import copy
import ujson as json
import urllib
import traceback
import random
import md5
import gc
import httplib


def read_char(s, start, limit, valid_set):
    return start + 1

def read_common(s, start, limit, valid_set):
    ptr = start + 1
    while (ptr < limit and s[ptr] in valid_set):
        ptr += 1
    return ptr
    
def read_word(s, start, limit, valid_set):
    ptr = start + 1
    while (ptr < limit):
        if s[ptr] == '"':
            return ptr + 1
        ptr += 1
    return ptr

def check_common(s):
    return s
    
def check_number(s):
    n = string.atof(s)
    return s

def check_word(s):
    if len(s) < 2 and s[0] != '"' and s[-1] != '"':
        raise Exception, 'invalid string value ' + s
    n = s[1:-1].replace("\\''", '"')
    return n

def build_split_map():
    key_set = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz0123456789')
    number_set = set('0123456789.')
    s_map = {
        'key' : {'type':'key', 'proc':read_common, 'set':key_set, 'check':check_common},
        'number' : {'type':'number', 'proc':read_common, 'set':number_set, 'check':check_number},
        'split' : {'type':'split', 'proc':read_char, 'set':None, 'check':check_common},
        'word' : {'type':'word', 'proc':read_word, 'set':None, 'check':check_word},
    }
    r = {}
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
        r[ch] = s_map['key']
    for ch in '0123456789':
        r[ch] = s_map['number']
    for ch in '=:,&|-+()':
        r[ch] = s_map['split']
    r['"'] = s_map['word']
    return r

def fsm_gather_key(word, data):
    m = {'type' : 'pair', 'key' : word, 'value' : [], 'word' : ''}
    data.append(m)

def fsm_gather_value(word, data):
    data[-1]['value'].append([word])
    
def fsm_gather_subvalue(word, data):
    data[-1]['value'][-1].append(word)

def fsm_expect_key(word, data):
    raise Exception, 'expect key at ' + word

def fsm_expect_equal(word, data):
    raise Exception, 'expect equal at ' + word

def fsm_expect_value(word, data):
    raise Exception, 'expect value at ' + word

def fsm_expect_endl(word, data):
    raise Exception, 'expect split or endl at ' + word

def build_fsm_map():
    return {
        'opened': {
            'key' : [fsm_gather_key, 'left'],
            'word' : [fsm_expect_key, ''],
            'number' : [fsm_expect_key, ''],
            'endl' : [fsm_expect_key, ''],
            '=' : [fsm_expect_key, ''],
            ':' : [fsm_expect_key, ''],
            ',' : [fsm_expect_key, ''],
            '&' : [fsm_expect_key, ''],
        },
        'left' : {
            'key' : [fsm_expect_equal, ''],
            'word' : [fsm_expect_equal, ''],
            'number' : [fsm_expect_equal, ''],
            'endl' : [fsm_expect_equal, ''],
            '=' : [None, 'right'],
            ':' : [fsm_expect_equal, ''],
            ',' : [fsm_expect_equal, ''],
            '&' : [fsm_expect_equal, ''],
        },
        'right' : {
            'key' : [fsm_gather_value, 'closed'],
            'word' : [fsm_gather_value, 'closed'],
            'number' : [fsm_gather_value, 'closed'],
            'endl' : [fsm_expect_value, ''],
            '=' : [fsm_expect_value, ''],
            ':' : [fsm_expect_value, ''],
            ',' : [fsm_expect_value, ''],
            '&' : [fsm_expect_value, ''],
        },
        'half' : {
            'key' : [fsm_gather_subvalue, 'closed'],
            'word' : [fsm_gather_subvalue, 'closed'],
            'number' : [fsm_gather_subvalue, 'closed'],
            'endl' : [fsm_expect_value, ''],
            '=' : [fsm_expect_value, ''],
            ':' : [fsm_expect_value, ''],
            ',' : [fsm_expect_value, ''],
            '&' : [fsm_expect_value, ''],
        },
        'closed' : {
            'key' : [fsm_expect_endl, ''],
            'word' : [fsm_expect_endl, ''],
            'number' : [fsm_expect_endl, ''],
            'endl' : [None, 'finished'],
            '=' : [fsm_expect_endl, ''],
            ':' : [None, 'half'],
            ',' : [None, 'right'],
            '&' : [None, 'opened'],
        },
    }

class service_base(object):
    _version = '0.60'
    _name = 'service_base'
    _status = None  # initing, resetting, updating, working, unworking

    _seq = 0
    _load = 0
    _limit = 0
    _auto_update = 0    # auto update time, min = 1 minute
    _next_update = None
    _heartbeat = 0      # 1/0 on/off
    
    _urls = ('/(.*)', 'search_base')    # default url

    _stat = {
        'init' : {
            'calling_counter' : 0,
            'success_counter' : 0,
            'error_counter' : 0,
            'peak_loading_time' : datetime.timedelta(0),
            'sum_loading_time' : datetime.timedelta(0),
        },
        'reset' : {
            'calling_counter' : 0,
            'success_counter' : 0,
            'error_counter' : 0,
            'peak_loading_time' : datetime.timedelta(0),
            'sum_loading_time' : datetime.timedelta(0),
            'calling_busy_counter' : 0,
            'calling_error_counter' : 0,
        },
        'update' : {
            'calling_counter' : 0,
            'success_counter' : 0,
            'error_counter' : 0,
            'peak_loading_time' : datetime.timedelta(0),
            'sum_loading_time' : datetime.timedelta(0),
            'calling_busy_counter' : 0,
            'calling_error_counter' : 0,
        },
        'get' : {
            'calling_counter' : 0,
            'success_counter' : 0,
            'error_counter' : 0,
            'peak_loading_time' : datetime.timedelta(0),
            'sum_loading_time' : datetime.timedelta(0),
            'calling_busy_counter' : 0,
            'calling_error_counter' : 0,
        },
        'post' : {
            'calling_counter' : 0,
            'success_counter' : 0,
            'error_counter' : 0,
            'peak_loading_time' : datetime.timedelta(0),
            'sum_loading_time' : datetime.timedelta(0),
            'calling_busy_counter' : 0,
            'calling_error_counter' : 0,
        },
        'load' : {
            'peak_load' : 0,
            'sum_load' : 0,
        },
    }

    def __init__(self):
        self._start_time = datetime.datetime.now()
        self._split_map = build_split_map()
        self._split_fsm = build_fsm_map()
        self._dir = os.path.dirname(os.path.realpath(__file__))
        self._dir_dump = os.path.join(self._dir, 'dump')
        self._dir_update = os.path.join(self._dir, 'update')
        self._dir_reset = os.path.join(self._dir, 'reset')
        self._dir_conf = os.path.join(self._dir, 'conf')
        self.__update_rem = int(random.random() * 60)
        self.__update_seq = 0
        self.__lock = threading.Lock()
        self.__heartbeat = None
        
        try:
            self._md5_base = md5.new(open(os.path.join(self._dir, 'service_base.py')).read()).hexdigest() 
            self._md5_interface = md5.new(open(os.path.join(self._dir, 'service_interface.py')).read()).hexdigest() 
        except Exception, e:
            self._md5_base = 'read error'
            self._md5_interface = 'read error'

        try:
            self._conf = self.json_load(open(os.path.join(self._dir_conf, 'service/service.ujson')))
        except Exception, e:
            self._conf = {}
            
        self.background_work('initing', [self._status], 'init', self.init_thread_proc)
        
    def get_urls(self):
        return self._urls

    def init_thread_proc(self):
        return {'result' : '0'}

    def reset_thread_proc(self):
        return {'result' : '0'}

    def update_thread_proc(self):
        return {'result' : '0'}

    def stat_result(self, stat, result):
        stat['success_time'] = datetime.datetime.now()
        stat['loading_time'] = stat['success_time'] - stat['calling_time']
        stat['sum_loading_time'] += stat['loading_time']
        if stat['loading_time'] > stat['peak_loading_time']:
            stat['peak_loading_time'] = stat['loading_time']
        stat['success_counter' if result['result'] == '0' else 'error_counter'] += 1
        if 'reason' in result:
            stat['last_reason'] = result['reason']

    def background_thread_proc(self, thread_proc, srv, stat_item):
        gc.disable()
        try:
            result = thread_proc()
        except Exception, e:
            result = {'result' : '1', 'reason' : str(e) + traceback.format_exc()}
        gc.enable()
        self.stat_result(srv._stat[stat_item], result)
        srv._status = 'working' if result['result'] == '0' else 'unworking'

    def time_thread_proc(self, seq):
        while True:
            time.sleep(6)
            if self.__update_seq != seq:
                return
            u = self._next_update
            if not u:
                return
            if u > datetime.datetime.now():
                continue
            self.web_get('update')
            self.set_auto_update(self._auto_update)
            return

    def set_auto_update(self, q):
        if type(q) is int:
            m = max(min(q, 1440), 0)
        elif type(q) is unicode:
            sm = q[1:]
            m = string.atoi(sm) if sm.isdigit() else 0
        else:
            m = int(0)
        self.__update_seq += 1
        self._auto_update = m
        self._next_update = None
        if m > 0:
            n = datetime.datetime.now()
            rem = (self.__update_rem - n.second) % 60
            rem += (60 if rem < 30 else 0) + (m - 1) * 60
            self._next_update = n + datetime.timedelta(seconds = rem)
            threading.Thread(target = self.time_thread_proc, args = (self.__update_seq,)).start()
        return {'result' : '0'}

    def heartbeat_proc(self, seq):
    
        while True:
            n = datetime.datetime.now()
            rem = (self.__update_rem - n.second) % 60
            rem += 60 if rem < 30 else 0
            time.sleep(rem)
            if not self._heartbeat:
                return
            
            heartbeat = self._conf.get('heartbeat', {})
            if not heartbeat:
                continue

            webtime = self._stat['get']['sum_loading_time'] + self._stat['post']['sum_loading_time']
            wt = ((webtime.days * 86400 + webtime.seconds) * 1000000 + webtime.microseconds) 
            
            calling = self._stat['get']['calling_counter'] + self._stat['post']['calling_counter']
            called = self._stat['get']['success_counter'] + self._stat['post']['success_counter']

            body = { 'data' : {
                'dir' : os.path.basename(self._dir),
                'name' : self._name,
                'status' : self._status,
                'seq' : self._seq,
                'cputime' : self.get_cputime() * 10000,
                'webtime' : wt,
                'calling' : calling,
                'called' : called,
                'load' : self._load,
                'webtime' : wt,
            } }
            
            try:
                c = httplib.HTTPConnection(heartbeat['host'], heartbeat['port'])
                c.request('POST', '/?stat=1', self.json_dumps(body))
                r = c.getresponse()
                if r.status == 200:
                    b = r.read()
                c.close()
            except Exception, e:
                pass

    def set_heartbeat(self, q):
        self._heartbeat = 1 if q else 0
        if self._heartbeat:
            if not self.__heartbeat:
                self.__heartbeat = threading.Thread(target = self.heartbeat_proc, args = (self.__update_seq,))
                self.__heartbeat.start()
        return {'result' : '0'}

    def background_work(self, new_status, valid_status, stat_item, thread_proc):
        stat = self._stat[stat_item]
        stat['calling_counter'] += 1
        stat['calling_time'] = datetime.datetime.now()
        status = self._status
        if status not in valid_status:
            stat['calling_busy_counter'] += 1
            return {'result':'1', 'reason':'service status error', 'status':status}
        self._status = new_status
        threading.Thread(target = self.background_thread_proc, args=(thread_proc, self, stat_item)).start()
        return {'result':'0', 'status':self._status}

    def web_get(self, name):
        gc.disable()
        r = None
        self._seq += 1

        if name:
            if (name == 'favicon.ico'):
                r = ''
            elif (name == 'info'):
                r = self.json_dumps(self.get_info())
            elif (name == 'status'):
                r = self.json_dumps(self.get_status())
            elif (name == 'reset'):
                r = self.json_dumps(self.background_work('resetting', ['working', 'unworking'], 'reset', self.reset_thread_proc))
            elif (name == 'update'):
                r = self.json_dumps(self.background_work('updating', ['working', 'unworking'], 'update', self.update_thread_proc))
            elif (name == 'autoupdate'):
                r = self.json_dumps(self.set_auto_update(web.ctx.query))
            elif (name == 'heartbeat'):
                r = self.json_dumps(self.set_heartbeat(web.ctx.query))
            if r is not None:
                gc.enable()
                return r
        r = self.json_dumps(self.web_task(name, self.default_get, 'get'))
        gc.enable()
        return r

    def web_post(self, name):
        print '777777777777777'
        gc.disable()
        self._seq += 1
        r = self.json_dumps(self.web_task(name, self.default_post, 'post'))
        gc.enable()
        return r

    def web_task(self, name, default_work, stat_item):
        stat = self._stat[stat_item]
        load = self._stat['load']
        stat['calling_counter'] += 1
        stat['calling_time'] = datetime.datetime.now()
        if self._status in ['initing', 'unworking']:
            stat['calling_error_counter'] += 1
            raise web.notfound()
        if self._limit > 0 and self._load > self._limit:
            stat['calling_busy_counter'] += 1
            raise web.notfound()

        self.__lock.acquire()
        self._load = self._load + 1
        self.__lock.release()
        load['sum_load'] += self._load
        if self._load > load['peak_load']:
            load['peak_load'] = self._load
        try:
            result = default_work(name)
        except Exception, e:
            result = {'result' : '1', 'reason' : str(e) + traceback.format_exc()} 
        
        self.__lock.acquire()
        self._load = self._load - 1
        self.__lock.release()
        
        self.stat_result(stat, result)
        return result
    
    def get_stat_called(self, stat):
        stat['called_counter'] = stat['success_counter'] + stat['error_counter']
        if stat['called_counter'] > 0:
            stat['avg_loading_time'] = stat['sum_loading_time'] / stat['called_counter']
        
    def get_stat_dict(self, stat):
        result = {}
        for k in stat:
            if type(stat[k]) is dict:
                result[k] = self.get_stat_dict(stat[k])
                continue
            if type(stat[k]) is list:
                result[k] = [self.get_stat_dict(x) for x in stat[k]]
                continue
            if stat[k]:
                result[k] = str(stat[k])
        return result

    def get_vmsize(self):
        peak, size = '', ''
        filename = '/proc/%d/status' % os.getpid()
        line_list = open(filename).read().split('\n')
        for line in line_list:
            sp = line.split('\t')
            if sp[0] == 'VmPeak:':
                n_list = sp[1].strip().split(' ')
                peak = str(int(n_list[0]) / 1024) + 'M'
            if sp[0] == 'VmSize:':
                n_list = sp[1].strip().split(' ')
                size = str(int(n_list[0]) / 1024) + 'M'
            if sp[0] == 'VmRSS:':
                n_list = sp[1].strip().split(' ')
                rss = str(int(n_list[0]) / 1024) + 'M'

        return peak, size, rss

    def get_cputime(self):
        filename = '/proc/%d/stat' % os.getpid()
        line_list = open(filename).read().split(' ', 20)
        return int(line_list[13]) + int(line_list[14])

    def get_info(self):
        peak, size, rss = self.get_vmsize()
        cputime = self.get_cputime()
        runtime = datetime.datetime.now() - self._start_time
        r = ((runtime.days * 86400 + runtime.seconds) * 1000000 + runtime.microseconds) / 10000

        return { 
            'name' : self._name,
            'version' : self._version,
            'status' : self._status,
            'load_now' : self._load,
            'load_limit' : self._limit,
            'sequence' : self._seq,
            'start_time' : str(self._start_time),
            'current_time' : str(datetime.datetime.now()),
            'run_time' : str(datetime.datetime.now() - self._start_time),
            'dir' : self._dir,
            'auto_update' : self._auto_update,
            'next_update' : str(self._next_update),
            'heartbeat' : self._heartbeat,
            'md5_base' : self._md5_base,
            'md5_interface' : self._md5_interface,
            'vmpeak' : peak,
            'vmsize' : size,
            'vmrss' : rss,
            'gc' : str(gc.get_count()),
            'cpu' : round(float(cputime * 100) / r, 4),
        }
        
    def get_status(self):
        stat = copy.copy(self._stat)
        self.get_stat_called(stat['reset'])
        self.get_stat_called(stat['update'])
        self.get_stat_called(stat['get'])
        self.get_stat_called(stat['post'])
        if stat['get']['called_counter'] > 0 or stat['post']['called_counter'] > 0:
            stat['load']['avg_load'] = float(stat['load']['sum_load']) / (stat['get']['called_counter'] + stat['post']['called_counter'])
        return { 'base' : {
            'info' : self.get_info(),
            'stat' : self.get_stat_dict(stat),
        } }

    def default_get(self, name):
        return {'result' : '0'}

    def default_post(self, name):
        print 'wwwwwwwwwwwwwww'
        return {'result' : '0'}

    def json_dumps(self, obj):
        return json.dumps(obj, ensure_ascii = False)
        
    def json_dump(self, data, fp):
        return json.dump(data, fp, ensure_ascii = False)

    def json_loads(self, s):
        return json.loads(s)

    def json_load(self, fp):
        return json.load(fp)

    def _str_to_word(self, us):
        ptr = 0
        limit = len(us)
        r = []
        while ptr < limit:
            line = self._split_map[us[ptr]]
            nptr = line['proc'](us, ptr, limit, line['set'])
            w = us[ptr : nptr]
            v = line['check'](w)
            r.append({'word' : w, 'value' : v, 'type' : line['type']})
            ptr = nptr
        if len(r) == 0:
            raise Exception, 'url query is empty'
        return r    

    def _word_to_value(self, lst):
        rdata = copy.copy(lst)
        rdata.append({'type':'endl', 'word':'endl', 'value':'endl'})
        data = []
        status = 'opened'
        for line in rdata:
            type = line['type']
            word = line['word']
            value = line['value']
            if type in ('key', 'number', 'word', 'endl'):
                event = type
            elif type == 'split' and word in ('=', ':', ',', '&'):
                event = word
            else:
                raise Exception, 'invalid word at ' + word
            fsm = self._split_fsm[status][event]
            if fsm[0]:
                fsm[0](value, data)
            status = fsm[1]
            if status == 'finished':
                return data
            if word != '&':
                data[-1]['word'] += word
        raise Exception, 'not expect here'

    def _query_to_str(self):
        q = web.ctx.query
        if len(q) <= 1:
            raise Exception, 'url is empty'
        return urllib.unquote(q[1:].encode('utf8')).decode('utf8')

    def query_to_str(self):
        try:
            return {'result' : '0', 'type' : 'query_string', 'data' : self._query_to_str()}
        except Exception, e:
            return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}
        
    def str_to_word(self, s):
        try:
            return {'result' : '0', 'type' : 'word_list', 'data' : self._str_to_word(s)}
        except Exception, e:
            return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}
    
    def word_to_value(self, lst):
        try:
            return {'result' : '0', 'type' : 'pair_list', 'data' : self._word_to_value(lst)}
        except Exception, e:
            return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}
        
    def str_to_value(self, s):
        try:
            return {'result' : '0', 'type' : 'pair_list', 'data' : self._word_to_value(self._str_to_word(s))}
        except Exception, e:
            return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}

    def query_to_word(self):
        try:
            return {'result' : '0', 'type' : 'word_list', 'data' : self._str_to_word(self._query_to_str())}
        except Exception, e:
            return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}
        
    def query_to_value(self):
        try:
            return {'result' : '0', 'type' : 'pair_list', 'data' : self._word_to_value(self._str_to_word(self._query_to_str()))}
        except Exception, e:
            return {'result' : '1', 'reason' : str(e) + traceback.format_exc()}

    def get_sync_list(self, p):
        try:
            file_list = os.listdir(p)
            r_list = []
            for fn in file_list:
                if fn[-5:] == '.sync':
                    dfn = fn[:-5]
                    if os.path.exists(os.path.join(p, dfn)):
                        r_list.append(dfn)
            r_list.sort()
            return r_list
        except Exception, e:
            return []
        
    def del_sync_list(self, p, r_list):
        for fn in r_list:
            cmd = 'rm -f %s' % os.path.join(p, fn)
            cmd2 = cmd + '.sync'
            try:
                os.system(cmd2)
                os.system(cmd)
            except Exception, e:
                pass
        
if __name__ == "main": 
    print "service_base done"
        
