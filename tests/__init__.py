# -*- coding: utf-8 -*-
"""
    __init__


    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class ViewDependsTestCase(unittest.TestCase):
    '''
    Test View and Depends for module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_tutorial')

    @unittest.skip("Skip this since there are no views")
    def test0005views(self):
        '''
        Test views.
        '''
        test_view('nereid_tutorial')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(ViewDependsTestCase),
    ])

    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
