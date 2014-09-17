"""Test runner for the complete test suite."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest

import test_core
import test_ddl
import test_ddl_constraints
import test_dml
import test_select
import test_geo
import test_types

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_core.suite())
    suite.addTest(test_ddl.suite())
    suite.addTest(test_ddl_constraints.suite())
    suite.addTest(test_dml.suite())
    suite.addTest(test_select.suite())
    suite.addTest(test_geo.suite())
    suite.addTest(test_types.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
