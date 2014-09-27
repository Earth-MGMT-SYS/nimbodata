"""Module provides ZFS filesystem as a Nimbodata entity."""
# Copyright (C) 2014  Bradley Alan Smith

import subprocess

import common.errors as errors
import common.entities.prototype as base_ent

class Diskspace(base_ent.Entity):
    
    objid_prefix = 'dsk'
    
    def _issue_command(self,command,target=None):
        if target is self:
            argz = ['sudo','zfs',command,self.fqn,target]
        elif target is None and command == 'list':
            argz = ['sudo','zfs',command,self.parent_objid]
        elif target is None:
            argz = ['sudo','zfs',command,self.fqn]
        return subprocess.check_output(argz)
    
    def _by_name(self,name):
        self.objid = name
        self.parent_objid = 'box'
        self.fqn = 'box/' + name
        return self.objid
        
    def create(self,diskid):
        self.objid = diskid
        self.parent_objid = 'box'
        self.fqn = 'box/' + diskid
        self._issue_command('create')
        return self
        
    def snapshot(self,snapid):
        self._issue_command('create',snapid)
        return self
    
    def listing(self):
        p = subprocess.check_output(['sudo','zfs','list'])
        rows = p.split('\n')
        header = [x.lower() for x in rows.pop(0).split()]
        return [dict(zip(header,row.split())) for row in rows[:-1]]
        
    def drop(self):
        argz = ['sudo','zfs','destroy',self.fqn]
        p = subprocess.check_output(argz)
        return True
