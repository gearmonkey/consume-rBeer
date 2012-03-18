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
import datetime

from Review import Review

class Beer(object):
    """
    metadata around a beer, and it's ratings
    """
    beer_uri = "http://www.ratebeer.com/beer/beer_name/{beer_id}/"
    ratings_uri = "http://www.ratebeer.com/Ratings-Who.asp?BeerID={beer_id}"
    ratings_regex = re.compile(r'<a href="/ViewUser\.asp\?UserID=(?P<userid>\d*)" target="_blank">(.*?)</a> \(<i><a href="/beer/beer_name/(\d*)/(?P=userid)/" target="_blank">Rating - (.*?)</a></i>\)')
    
    reviews_regex = re.compile(r'<IMG style="max-width: 60px; max-height: 60px; height: auto; width: auto;" width= "60" src="/userpics/(?P<username>\S*?)\.jpg" class="curvy"></div><div style="display:inline; padding: 0px 0px; font-size: 24px; font-weight: bold; color: #036;" title="(?P<rating>\d\.?\d?) out of 5\.0">(?P=rating)</div><strong>&nbsp;&nbsp;<small> AROMA </small><big style="color: #999;">(\d\d?)/10</big>&nbsp;&nbsp;<small> APPEARANCE </small><big style="color: #999;">(\d)/5</big>&nbsp;&nbsp;<small> TASTE </small><big style="color: #999;">(\d\d?)/10</big>&nbsp;&nbsp;<small> PALATE </small><big style="color: #999;">(\d)/5</big>&nbsp;&nbsp;<small> OVERALL </small><big style="color: #999;">(\d\d?)/20</big></strong></div><small style="color: #666666; font-size: 12px; font-weight: bold;"><A HREF="/user/(\d*?)/">(?P=username)&nbsp;\(\d*?\)</A></I> - (.*?) - (.*?)</small><BR><div style="padding: 20px 10px 20px 0px; border-bottom: 1px solid #e0e0e0;">(.*?)</div>', flags=re.DOTALL)
    
    get_metadata = {'name': re.compile(r'<div class="user-header"><h1>(.*?)</h1></div>'),
                    'abv': re.compile(r'<abbr title="Alcohol By Volume">ABV</abbr>: <big style="color: #777;"><strong>(.*?)%</strong></big>'),
                    'mean': re.compile(r'MEAN: <big style="color: #777;"><strong>(\d\.?\d?)/5\.0</strong></big>') ,
                    'weighted_score': re.compile(r'<a name="real average" title="The weighted average, (\d\.?\d*?), is the Bayesian mean of all qualified ratings for this beer" >WEIGHTED AVG: <big style="color: #777;"><strong>\d\.?\d*?</strong></big></a>'),
                    'overall_percentile': re.compile(r'<td align=center colspan=2 style="background-color: #036; font-size: 72px; font-weight: bold; color: #fff; padding: 10px;" title="(\d?\d?\d\.?\d*?): This figure represents a beer\x92s performance relative to all beers on an adjusted percentile basis\. Find out more in the FAQ\."'),
                    'style_percentile': re.compile(r'<td align=center style="background-color: #66A212; font-size: 28px; font-weight: bold; color: #fff; padding: 10px;" colspan=2 title="(\d?\d?\d\.?\d*?): This figure represents a beer\x92s performance relative to its peers in the same beer style category on an adjusted percentile basis. Find out more in the FAQ\.">'),
                    'total_ratings': re.compile(r'RATINGS: </abbr><big style="color: #777;"><b>(\d+)</b></big>'),
                    'brewery_and_style': re.compile(r'<div style="padding-bottom: 7px; line-height: 1.5;"><big>Brewed by <b><a href="/brewers/.*?/(\d+)/">.*?</A></b></big><br>Style: <a href="/beerstyles/.*?/(\d+)/">.*?</a><br>.*?</div>')}
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
    def __str__(self):
        return "'{0}' from {1}".format(self.name, Beer.beer_uri.format(beer_id=self.uid))
    
    def fetch_beer_page(self, page=None):
        """
        returns html string of the beer page
        """
        if page:
            return urllib2.urlopen(Beer.beer_uri.format(beer_id=self.uid)+'1/{0}/'.format(page)).read()
        else:
            return urllib2.urlopen(Beer.beer_uri.format(beer_id=self.uid)).read()
    
    def parse_metadata(self, raw_page=None):
        """
        scrapes the beer metadata out of a beer's raw_page string
        Note! overrides existing metadata
        """
        if not raw_page:
            raw_page = self.fetch_beer_page()
        self.name = Beer.get_metadata['name'].findall(raw_page)[0]
        self.abv = float(Beer.get_metadata['abv'].findall(raw_page)[0])
        self.mean_score = float(Beer.get_metadata['mean'].findall(raw_page)[0])
        self.weighted_score = float(Beer.get_metadata['weighted_score'].findall(raw_page)[0])
        self.overall_percentile=float(Beer.get_metadata['overall_percentile'].findall(raw_page)[0])
        self.style_percentile=float(Beer.get_metadata['style_percentile'].findall(raw_page)[0])
        self.total_ratings=int(Beer.get_metadata['total_ratings'].findall(raw_page)[0])
        self.brewery_id=int(Beer.get_metadata['brewery_and_style'].findall(raw_page)[0][0])
        self.style_id=int(Beer.get_metadata['brewery_and_style'].findall(raw_page)[0][1])
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

    def scrape_user_comment_list(self, raw_page=None):
        if not raw_page:
            raw_page = self.fetch_beer_page()
        self.reviews = []
        try:
            self.total_ratings
        except AttributeError:
            self.parse_metadata(raw_page)
        page = 1
        while len(self.reviews) < self.total_ratings:
            if page != 1:
                raw_page = self.fetch_beer_page(page=page)
            self.reviews +=[Review(beer_uid=self.uid, user_uid=int(user_id),
                                    brewery_uid =self.brewery_id, topline_score=float(topline_score),
                                    aroma_score=int(aroma), apperance_score=int(apperance),
                                    taste_score=int(taste), palete_score=int(palete),
                                    overall_score=int(overall), user_loc=user_loc,
                                    date = datetime.datetime.strptime(date_str, '%b %d, %Y').date(),
                                    comment = comment) for (username, topline_score, aroma, apperance, 
                                                        taste, palete, overall, user_id, user_loc, 
                                                        date_str, comment) in \
                                                                Beer.reviews_regex.findall(raw_page)]
            page += 1
        
class BeerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()