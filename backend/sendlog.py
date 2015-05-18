import urllib
import urllib2
import json
import sys
import os
import re
import time
from datetime import datetime, timedelta

def sendto8017(values):
    url='http://192.168.0.24:8027/test?grade="1"'
    #values ={'user':'Smith','passwd':'123456'}
    jdata = json.dumps(values)
    req = urllib2.Request(url, jdata)
    response = urllib2.urlopen(req)
    return response.read()

def getlog(one_second_before):
    commend = "tail -5000 /home/nginxlog/accesslog/service.kuxun.cn/hotel/price/access.log | egrep 'hotel_search' | egrep '%s'" % one_second_before
    output = os.popen(commend)
    return output.read()

def analyzelog(logdata):
    citydict = {}
    datas = logdata.split('\n')
    for each in datas:
        print each, '222222222222222222222222222'
        #rawcity = re.findall('city=\\x22(.*?)\\x22',each)
        rawcity = re.findall('city=\\\\x22(.*?)\\\\x22&',each)
        print rawcity, '***********'
        if len(rawcity) > 0:
            if citydict.get(rawcity[0], ' ') == ' ':
                citydict[rawcity[0]] = 1
            else:
                citydict[rawcity[0]] += 1
    return citydict

def main():
    former_one_second_before = '0'
    while True:
        a = time.localtime(time.time())
        print a, '222222222'
        hour, minute, second = a[3], a[4], a[5]
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
        print one_second_before, 'aaaaaaaaa'
        if former_one_second_before == one_second_before:
            time.sleep(0.5)
            print 'tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt'
            continue

        logdata = getlog(one_second_before)
        print logdata
        citydict = analyzelog(logdata)
        print citydict, 'bbbbbbbbbbb'


        values ={'user':'Smith','passwd':'123456'}
        try:
            ret = sendto8017(citydict)
        except:
            pass
        print ret, '11111111'
        time.sleep(0.5)
        former_one_second_before = one_second_before


if __name__ == "__main__":
    main()
