
import os
import csv
from codecs import EncodedFile
import StringIO

import requests

from core.pg.datatypes import Text

def _process_file(text):
    rdr = csv.reader(row for row in StringIO.StringIO(text) if row[0] != '#')
    header = rdr.next()
    rows = [x for x in rdr]
    return header,rows

class UpdateWebDatabase(object):
    """A database drawn from CSV files."""
    
    def __init__(self,name,urls,table_factory,single_table=False):
        self.name, self.urls, self.table_factory = name, urls, table_factory
    
    def tables(self):
        out, uq = list(), set()
        for x in self.urls:
            if x[0] not in uq:
                out.append(self.table_factory(*x))
                uq.add(x[0])
        return out
        
    def sources(self):
        return (self.table_factory(*x) for x in self.urls)

class UpdateWebTable(object):
    """A table from a CSV URL."""
    
    def __init__(self,name,url):
        self.name, self.url = name, url
        print url
        r = requests.get(url)
        if r.status_code == 404:
            self.header, self.rows = None, None
            return # Logit later.
        self.header, self.rows = self.process_result(r.text)
        
    @property
    def columns(self):
        return [{'name':x,'datatype':Text} for x in self.header]
    
    def select(self):
        return rows
        
    def asfile(self):
        outfile = StringIO.StringIO()
        cwrite = csv.writer(outfile)
        if self.rows is None:
            return None
        for row in self.rows:
            cwrite.writerow(row)
        return outfile

    def process_result(self, text):
        rdr = csv.reader((row for row in StringIO.StringIO(text) if row[0] != '#'),
            dialect='excel')
        header = rdr.next()
        if len(header) == 1:
            rdr = csv.reader((row for row in StringIO.StringIO(text) if row[0] != '#'),
            dialect='excel-tab')
            header = rdr.next()
        rows = [x for x in rdr]
        return header,rows
