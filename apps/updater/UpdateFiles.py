
import os
import csv
from codecs import EncodedFile
import StringIO

from core.pg.datatypes import Text

class UpdateFileDatabase(object):
    """A database drawn from CSV files."""
    
    def __init__(self,name,infiles,table_factory):
        self.name, self.infiles, self.table_factory = name, infiles, table_factory
    
    def tables(self):
        retVal = []
        for fname,fpath in self.infiles:
            tablename = os.path.splitext(fname)[0]
            f = EncodedFile(open(fpath,'rb'),'utf-8','utf-8','ignore')
            c = csv.reader(f)
            retVal.append(self.table_factory(fname,fpath))
        return retVal
        
    sources = tables

class UpdateFileTable(object):
    """A table from a CSV file."""
    
    def __init__(self,fname,fpath):
        self.fname, self.fpath = fname, fpath
        self.name = os.path.splitext(fname)[0]
        
    @property
    def columns(self):
        f = EncodedFile(open(self.fpath,'rb'),'utf-8','utf-8','ignore')
        return [{'name':x,'datatype':Text} for x in csv.reader(f).next()]
        
    def select(self):
        src_file = EncodedFile(open(self.fpath,'rb'),'utf-8','utf-8','ignore')
        src_file.next()
        reader = csv.reader(src_file)
        return list(reader)
        
    def asfile(self):
        header,rows = self.process_result(EncodedFile(open(self.fpath,'rb'),'utf-8','utf-8','ignore'))
        f = StringIO.StringIO()
        w = csv.writer(f)
        for row in rows: w.writerow(row)
        return f

    def process_result(self,infile):
        r = csv.reader(infile)
        header = r.next()
        return header,(x for x in r)
        
