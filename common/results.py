"""Module implements the container objects for select results and rows."""
# Copyright (C) 2014  Bradley Alan Smith

import datetime
import json

import datatypes
import datatypes.fallback_json as fallback_json

fallback_json = fallback_json.fallback_json


class Row(object):
    """ Simple wrapper with some special methods for a row """
    
    def _conv_val(self,datatype,value):
        if datatype == 'Json':
            return value
        try:
            return getattr(datatypes,datatype)(value)
        except (AttributeError,TypeError):
            return value
    
    def __init__(self,header,decoder,items):
        if isinstance(items,dict):
            new_items = []
            for h in header:
                new_items.append(items[h['name']])
            items = new_items
        
        self.data = [
            self._conv_val(h['datatype'],v) for h,v in zip(header,items)
        ]
        
        self.header = header
        self.decoder = decoder
    
    @property
    def row_dict(self):
        return dict(zip((x['name'] for x in self.header),self.data))
    def __len__(self):
        return len(self.data)
    def __str__(self):
        return json.dumps(self.data)
    def __getitem__(self,key):
        try:
            return self.data[key]
        except (TypeError,IndexError):
            try:
                return self.data[self.decoder[key]]
            except KeyError:
                # So I don't have to implement an interator
                raise IndexError
        except KeyError:
            for i,x in enumerate(self.header):
                if x['weight'] == key:
                    return self.data[x['name']]

class Results(object):
    """ Simple wrapper with some special methods to hold results """
    def __init__(self, colinfo, rows, viewinfo=None):        
        self.data = {}
        self.data['header'] = colinfo
        if viewinfo is not None:
            self.data['info'] = viewinfo
        self.header = self.data['header']
        self.decoder = dict((x['name'],i) for i,x in enumerate(self.data['header']))
        self.data['rows'] = rows
        self.rows = rows
    def __getitem__(self,key):
        return Row(self.header,self.decoder,self.rows[key])
    def __iter__(self):
        return (Row(self.header,self.decoder,x) for x in self.rows)
    def __len__(self):
        try:
            return len(self.data['rows'])
        except TypeError:
            return self.data['rows'].rowcount
    def toJSON(self):
        return self.data
    def __str__(self):
        return json.dumps(self.data,indent=4,sort_keys=True,default=fallback_json)
    def __repr__(self):
        return json.dumps(self.data)
