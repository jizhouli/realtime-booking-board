#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Yan Antao
# Date: 2012/10/11

import os
import sys
import web
import service_interface

app = web.application(service_interface.get_instance().get_urls(), globals()) 

class search_base(object):
    def __init__(self):
        self._srv = service_interface.get_instance()

    def GET(self, name):
        return self._srv.web_get(name)

    def POST(self, name):
        print '222222222222222222'
        return self._srv.web_post(name)

if __name__ == "__main__": 
    app.run()
