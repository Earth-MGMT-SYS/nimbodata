"""Module for performance testing nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest,time,datetime
import sys
import time

import config_cloud as cfg

sys.path.append('../')

from core.pg.datatypes import Text,Integer

target = 'local'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.starttime = time.time()
        self.startclock = time.clock()
        return self

    def __exit__(self, *args):
        self.endtime = time.time()
        self.endclock = time.clock()
        self.secstime = self.endtime - self.starttime
        self.secsclock = self.endclock - self.startclock
        self.msecstime = self.secstime * 1000  # millisecs
        self.msecsclock = self.secsclock * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs


class fixture(object):

    def __init__(self):
        self.setUp()

    def setUp(self):
        """Create the database, a table and insert some values."""
        try:
            self.db = cloud.create_database('selectdb')
        except cc.RelationExists:
            cloud.Database('selectdb').drop()
            self.db = cloud.create_database('selectdb')
        cols = [
            {'name':'pk','datatype':Text,'primary_key':True},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = cloud.create_table(self.db,'testTable',cols)
        self.values = [
            ('frank',2,'apple'),
            ('jerry',5,'orange'),
            ('ann',7,'fig'),
            ('francine',9,'tomato'),
        ]
        
        self.rowids = self.table.insert(self.values)
        
    def tearDown(self):
        """Drop the database."""
        self.db.drop()
        
    def run(self):
        result = cloud.select(self.table)

n = 10

f = fixture()
running_time = 0
running_clock = 0
mintime = None
maxtime = 0
minclock = None
maxclock = 0
for i in range(n):
    with Timer() as t:
        f.run()
    running_time += t.msecstime
    running_clock += t.msecsclock
    if mintime is None:
        mintime = t.msecstime
    elif t.msecstime < mintime:
        mintime = t.msecstime
    elif t.msecstime > maxtime:
        maxtime  = t.msecstime
    
    if minclock is None:
        minclock = t.msecsclock
    elif t.msecsclock < minclock:
        minclock = t.msecsclock
    elif t.msecsclock > maxclock:
        maxclock  = t.msecsclock
f.tearDown()
    
print "Average: ", running_clock / n, running_time / n, (running_time - running_clock) / n
print "Min: ", minclock, mintime, mintime - minclock
print "Max: ", maxclock, maxtime, maxtime - maxclock



