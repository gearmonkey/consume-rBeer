#!/usr/bin/env python
# encoding: utf-8
"""
Review.py

Created by Benjamin Fields on 2012-01-07.
Copyright (c) 2012 . All rights reserved.
"""

import sys
import os
import unittest


class Review:
    def __init__(self, *args, **kwargs):
        """any of the following attributes can be set at initialisation by kwarg:
        beer_uid (int)
        user_uid (int)
        brewery_uid (int)
        topline_score (float [0,5.0])
        aroma_score (int [0,10])
        apperance_score (int [0,5])
        taste_score (int [0,10])
        palete_score (int [0,5])
        overall_score (int [0,20])
        loc (str) (unicode optimal)
        date (datetime.date)
        comment (str) (unicode optimal)
        """
        self.beer_uid = kwargs.get(beer_uid):
        self.user_uid = kwargs.get(user_uid)
        self.brewery_uid = kwargs.get(brewery_uid)
        self.topline_score = kwargs.get(topline_score)
        self.aroma_score = kwargs.get(aroma_score)
        self.apperance_score = kwargs.get(apperance_score)
        self.taste_score = kwargs.get(taste_score)
        self.palete_score = kwargs.get(palete_score)
        self.overall_score = kwargs.get(overall_score)
        self.loc = kwargs.get(loc)
        self.date = kwargs.get(date)
        self.comment = kwargs.get(comment)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()