"""Module implements a datamodel which provies nested tree navigation."""
# Copyright (C) 2014  Bradley Alan Smith

    
class Model(object):
    
    def __init__(self,rows):
        """Instantiates an MVC datamodel from a list of entities/dicts."""
        self.root, self.index, self.rows = self.expand(rows)
        
    def __getitem__(self,key):
        return self.model[key]
        
    def __setitem__(self,key,val):
        self.model[key] = val
    
    def expand(self,rows):
        """Given a list of objinfo dicts returns the model, index and rows."""
        root = {}
        index = {}
        outrows = []
        
        for row in rows:
            node = api.get_byid(row['objid'])
            index[node.objid] = node
            outrows.append(node)
            try:
                index[row['parent_objid']].children.append(node)
            except AttributeError:
                index[row['parent_objid']].children = [node]
            except KeyError:
                root[node.objid] = node
                        
        return root, index, outrows
    
    def __iter__(self):
        """Iterates via self.rows."""
        for x in self.rows:
            yield x
            
    def __len__(self):
        return len(self.root.keys())
