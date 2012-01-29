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
import urllib2
import re
import logging


class Beer:
    """
    metadata around a beer, and it's ratings
    """
    beer_uri = "http://www.ratebeer.com/beer/beer_name/{beer_id}/"
    ratings_uri = "http://www.ratebeer.com/Ratings-Who.asp?BeerID={beer_id}"
    ratings_regex = re.compile(r'<a href="/ViewUser\.asp\?UserID=(?P<userid>\d*)" target="_blank">(.*?)</a> \(<i><a href="/beer/beer_name/(\d*)/(?P=userid)/" target="_blank">Rating - (.*?)</a></i>\)')
    name_regex = re.compile(r'<TITLE>(.*)</TITLE>')
    def __init__(self, beer_uid, name=None, abv=None, mean_score=None, overall_percentile=None,
                style_percentile=None, total_ratings=None, brewery_id=None):
        self.uid = int(beer_uid)
        self.name = name
        if abv:
            self.abv = float(abv)
        if mean_score:
            self.mean_score = float(mean_score)
        if overall_percentile:
            self.overall_percentile=float(overall_percentile)
        if style_percentile:
            self.style_percentile=float(style_percentile)
        if total_ratings:
            self.total_ratings=int(total_ratings)
        if brewery_id:
            self.brewery_id=int(brewery_id)
    
    def fetch_beer_page(self):
        """
        returns html string of the beer page
        """
        return urllib2.urlopen(Beer.beer_uri.format(beer_id=self.uid)).read()
    
    def parse_metadata(self, raw_page=None):
        """
        scrapes the beer metadata out of a beer's raw_page string
        """
        if not raw_page:
            raw_page = self.fetch_beer_page()
        results = Beer.name_regex.findall(raw_page);
        if len(results) > 0:
            self.name = results[0]
        
    def fetch_rating_page(self):
        """
        returns the html string of the minimized rating list
        """
        return urllib2.urlopen(Beer.ratings_uri.format(beer_id=self.uid)).read()
        
    def scrape_user_rating_list(self, raw_page=None):
        """
        scrapes the minimized user comment list (basically just ratings), 
        creating a list of tuples in self.ratings where each tuple takes the form
        (username, userID, beerRating)
        username is a str, userID an int, and beerRating a float
        the prime advantage of this over scrape_user_comment_list is that it 
        takes only one http GET to fetch this entire list, while gathering full
        comments and ratings by beer takes N/10 GETs where N is the number of 
        comments (though there may be undocumented means of increasing the page size)
        """
        if not raw_page:
            raw_page = self.fetch_rating_page()
        self.ratings = [(username, int(userID), float(beerRating)) 
                        for (userID, username, beerID, beerRating) in Beer.ratings_regex.findall(raw_page)]
        
class BeerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
