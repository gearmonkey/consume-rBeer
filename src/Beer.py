#!/usr/bin/env python
# encoding: utf-8
"""
Beer.py

Created by Benjamin Fields on 2012-01-07.
Copyright (c) 2012 . All rights reserved.
"""

import sys
import os
import unittest


class Beer:
    """
    metadata around a beer, and it's ratings
    """
    def __init__(self, beer_uid, name=None, abv=None, mean_score=None, overall_percentile=None,
                style_percentile=None, total_ratings=None, Brewery_id=None):
        self.uid = beer_uid
        
        

class BeerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()