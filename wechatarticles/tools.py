# coding: utf-8

import time

class tools(object):

    def  __init__(self):
        pass
    
    @staticmethod
    def timestamp2date(timestamp):
        time_array = time.localtime(timestamp)
        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return datetime