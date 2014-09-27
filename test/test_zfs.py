"""Module tests the instantiation of database entities."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
import subprocess

import config_cloud as cfg

sys.path.append('../')

from core.zfs import diskspace

@unittest.skip('skip')
class TestZFS(unittest.TestCase):
    """Test the ZFS engine functionality."""
    
    def setUp(self):
        """Set up the disk space, try to drop and try again if trouble."""
        try:
            self.disk = diskspace.Diskspace().create('test')
        except subprocess.CalledProcessError:
            self.disk = diskspace.Diskspace('test').drop()
            self.disk = diskspace.Diskspace().create('test')
        
    def tearDown(self):
        """Drop the diskspace."""
        self.disk.drop()
    
    #@unittest.skip('skip')
    def test_create(self):
        """Can we create a diskspace?"""
        disks = self.disk.listing()
        disknames = [x['name'] for x in disks]

if __name__ == '__main__':
    unittest.main()
