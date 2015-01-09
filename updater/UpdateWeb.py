
import os
import csv
from codecs import EncodedFile
import StringIO
import zipfile
import tarfile
import tempfile

import requests
import pycurl
import xlrd

from nimbodata.core.pg.datatypes import Text

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
        for x in self.urls:
            try:
                yield self.table_factory(*x)
            except StopIteration:
                continue

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
        try:
            return [{'name':x,'datatype':Text} for x in self.header]
        except TypeError:
            return []
    
    def select(self):
        return rows
        
    def asfile(self):
        outfile = EncodedFile(StringIO.StringIO(),'ascii',errors='ignore')
        cwrite = csv.writer(outfile)
        if self.rows is None:
            return None
        for row in self.rows:
            try:
                cwrite.writerow(row)
            except UnicodeEncodeError:
                print "row error" # Ignore bad names, grumble grumble
                continue
        return outfile

    def process_result(self, text):
        rdr = csv.reader((row for row in StringIO.StringIO(text) if row[0] != '#'),
            dialect='excel')
        try:
            header = rdr.next()
        except StopIteration:
            return None, None
            
        if len(header) == 1:
            rdr = csv.reader((row for row in StringIO.StringIO(text) if row[0] != '#'),
                dialect='excel-tab')
            header = rdr.next()
        rows = [x for x in rdr]
        return header,rows
        
class UpdateWebXLTable(UpdateWebTable):
    """A table from a XLS URL."""
    
    def __init__(self,name,url):
        self.name, self.url = name, url
        print url
        r = requests.get(url)
        if r.status_code == 404:
            self.header, self.rows = None, None
            return # Logit later.
        self.header, self.rows = self.process_result(r.content)
    
    def process_result(self, content):
        f, temppath = tempfile.mkstemp()
        f = os.fdopen(f,'w')
        f.write(content)
        f.close()
        wb = xlrd.open_workbook(temppath)
        worksheet = wb.sheet_by_name('WYS Overview')
        out_rows = []
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = -1
        header = None
        while curr_row < num_rows:
            curr_row += 1
            row = worksheet.row(curr_row)
            if header is None:
                header = []
                curr_cell = -1
                while curr_cell < num_cells:
                    curr_cell += 1
                    # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                    cell_type = worksheet.cell_type(curr_row, curr_cell)
                    cell_value = worksheet.cell_value(curr_row, curr_cell)
                    header.append(cell_value)
                continue
            curr_cell = -1
            row = []
            while curr_cell < num_cells:
                curr_cell += 1
                # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                cell_type = worksheet.cell_type(curr_row, curr_cell)
                cell_value = worksheet.cell_value(curr_row, curr_cell)
                row.append(cell_value)
            out_rows.append(row)
        os.remove(temppath)
        return header,out_rows

class UpdateZipWebTable(UpdateWebTable):
    """A table from a CSV in a zip or tar file."""
    
    def __init__(self,name,url):
        tempdir = tempfile.mkdtemp()
        buf = StringIO.StringIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buf)
        curl.perform()
        curl.close()
        try:
            with zipfile.ZipFile(buf,'r') as myzip:
                myzip.extractall(tempdir)
        except:
            buf.seek(0)
            with tarfile.TarFile(fileobj=buf,mode='r') as mytar:
                mytar.extractall(tempdir)
        
        fname = [ f for f in os.listdir(tempdir)
            if os.path.splitext(f)[1] == '.csv'][0]
        
        self.name = name     
        with open(os.path.join(tempdir,fname),'r') as tmpfile:
            self.header, self.rows = self.process_result(tmpfile.read())
