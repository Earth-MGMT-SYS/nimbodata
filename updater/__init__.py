
import subprocess

import sys
import csv
from pprint import pprint


#csv.field_size_limit(sys.maxsize)

import psycopg2

from UpdateFiles import *
from UpdateWeb import *
from UpdateShapefiles import *

target = 'local'
user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

if target == 'local':
    import nimbodata.cloud as cc
    cloud = cc.Cloud(user)
elif target == 'rest':
    import nimbodata.client.pyclient as cc
    cloud = cc.connect("http://localhost:5000",user)
    
import nimbodata.common.errors as errors

class Updater(object):
    """Update manager creates and/or updates a database based on a spec."""
    
    def __init__(self,source,db=None):
        self.source, self.db = source, db
    
    def create(self):
        """Create the database and all tables defined in the spec."""
        if self.db is None:
            try:
                self.db = cloud.create_database(self.source.name)
            except cc.RelationExists:
                cloud.Database(self.source.name).drop()
                self.db = cloud.create_database(self.source.name)

        try:            
            self.tables = {}
            for i,src_tbl in enumerate(self.source.tables()):
                self.tables[src_tbl.name] = self.db.create_table(src_tbl.name,src_tbl.columns)
        except errors.RelationExists:
            self.tables = {}
            for i,src_tbl in enumerate(self.source.tables()):
                self.tables[src_tbl.name] = self.db.Table(src_tbl.name)
        
        """
        self.tables = dict(
            (src_tbl.name,self.db.create_table(src_tbl.name,src_tbl.columns))
            for src_tbl in self.source.tables()
        )
        """
            
        return self.db
    
    def load(self):
        """Insert all data and add indexes."""
        self.update()
        for table in self.tables.values():
            geocols = table.geo_columns()
            for col in geocols:
                table.add_index(col)
                print "Added spatial index to: " + col['name']
    
    def update(self):
        """Insert all data in the spec."""
        errors = []
        i = 0
        for src in self.source.sources():
            i = i + 1
            try:
                ins_tbl = self.tables[src.name]
            except KeyError as e:
                if self.source.single_table:
                    ins_tbl = self.tables[self.source.single_table]
                else:
                    raise e
            print ins_tbl
            try:
                src_file = src.asfile()
            except subprocess.CalledProcessError as e:
                print e
                errors.append(e)
            if src_file is not None:
                ins_tbl.insert_file(src_file)
        
        print 'Number of errors vs total: ',len(errors), ' / ', i
        pprint(errors)
