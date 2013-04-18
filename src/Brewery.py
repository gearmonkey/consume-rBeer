#!/usr/bin/env python
# encoding: utf-8
"""
Brewery.py

Created by Benjamin Fields on 2012-01-07.
Copyright (c) 2012 . All rights reserved.
"""

import sys
import os
import unittest
import urllib2
import re
import logging


from Beer import Beer

class Brewery:
    """
    Basic manual instanciation can happen through __init__, but for standard 
    use via ratebeer scraping, creation of an instance should occur via the 
    static Brewery.parse
    """
    brewery_uri = "http://ratebeer.com/brewers/brewer_name/{brewery_id}/"
    regexes = {'name': re.compile(r'<span class=beerfoot>.*?<br><br></span><h1>(.*?)</h1>', flags=re.DOTALL),
            'type': re.compile(r'<font color="#666666">Type:(.*?)</font><br>'),
            'full_address': re.compile(r'<br><br><a href =".*?" target="new"><b>(.*?)<BR>(.*?)</b> <img'),
            'region' : re.compile(r'&gt; <a href="/beer/brewers/">Brewers</a> &gt;.*?&gt; <a href="(.*?)">(.*?)</a> &gt;'),
            'country': re.compile(r'&gt; <a href="/beer/brewers/">Brewers</a> &gt; (<a.*?>)?(.*?)(</a>)? &gt;'), 
            'url': re.compile(r'Web: <A HREF="(?P<url>.*?)" TARGET=_blank>.*?</A>'),
            'phone': re.compile(r'<IMG SRC="/images/phone.gif".*?>(.*?)<BR>'),
            'fb_url': re.compile(r'Facebook: <a href="http://www.facebook.com/(.*?)" target="_blank">.*?</a>'), 
            'beers': re.compile(r'<TR class=dataTableRow.*?><TD width="65%" style="border-left: 0px solid #d7d7d7;"><font size=4>&nbsp;</font><A HREF="/beer/.*?/(?P<beerID>\d*?)/">(.*?)</A> &nbsp; </TD><TD valign=top>.*?</TD><TD align="right">(<font color=#999999>)?(.*?)(</font>&nbsp;&nbsp;)?</TD><TD>(<font color=#999999>&nbsp;&nbsp;)?(.*?)(</font>&nbsp;&nbsp;)?</TD><TD align=center>(<b>)?(\d*?)(</b>&nbsp;&nbsp;)?</TD><TD align=center>(<b>)?(\d*?)(</b>&nbsp;&nbsp;)?</TD><TD align="right">(<font color=#999999>)?(\d*?)(</font>&nbsp;&nbsp;)?</TD>')} 
    
    def __init__(self, name=None, full_address=None, region=None,
                country=None, url=None, source_url=None, phone=None, 
                rb_id=None, img_url=None, fb_url=None, beers=[]):
        """
        provides a direct means of creating a brewery instance.
        """
        self.display_name = name
        self.full_address = full_address
        self.region = region
        self.country = country
        self.url = url
        self.phone = phone 
        self.fb_url = fb_url
        self.beers = beers
        
        #these will typically be filled in by the instaciating code directly
        if rb_id:       
            self.rb_id = int(rb_id)
        self.source_url = source_url

    
    def fetch_page(self):
        """
        returns the raw page source for a brewery page
        """
        return urllib2.urlopen(Brewery.brewery_uri.format(brewery_id=self.rb_id)).read()
    
    def parse(self, raw_page=None):
        """
        uses the html string (should be text from a brewery page on 
        rate beer) raw_page to populate brewery attributes
        """
        if not raw_page:
            raw_page = self.fetch_page()
        self.display_name = unicode(Brewery.regexes['name'].findall(raw_page)[0].strip(), encoding='utf-8')
        self.brewer_type = unicode(Brewery.regexes['type'].findall(raw_page)[0].strip(), encoding='utf-8')
        self.full_address = unicode(','.join(Brewery.regexes['full_address'].findall(raw_page)[0]), encoding='utf-8')
        try:
            self.region = unicode(Brewery.regexes['region'].findall(raw_page)[0][-1].strip(), encoding='utf-8')
        except IndexError:
            #if no region, leave it as None
            logging.warning('Unable to parse a region for {0}'.format(self.display_name))
        self.country = unicode(Brewery.regexes['country'].findall(raw_page)[0][1].strip(), encoding='utf-8')
        try:
            self.url = unicode(Brewery.regexes['url'].findall(raw_page)[0].strip(), encoding='utf-8')
        except IndexError:
            logging.warning('Unable to parse a url for {0}'.format(self.display_name))
        try:
            self.phone = unicode(Brewery.regexes['phone'].findall(raw_page)[0].strip(), encoding='utf-8')
        except IndexError:
            logging.warning('Unable to parse a phone for {0}'.format(self.display_name))
        try:
            self.fb_url = unicode(Brewery.regexes['fb_url'].findall(raw_page)[0], encoding='utf-8')
        except IndexError:
            logging.warning('Unable to parse a facebook url for {0}'.format(self.display_name))
        #beers = self._populate_beer_list(Brewery.regexes['beers'].findall(raw_page))
        
    def _populate_beer_list(self, beer_tuples):
        """
        given a list of beer tuples of the form
            (stuff)
        create an instance of the Beer class for & with each beer_tuple
        append the resulting instance to self.beer
        returns a list of these instances 
        """
        #mapping removes the formatting tag groups from each beer tuple
        return [Beer(b[0],b[1],b[3],b[6],b[9],b[12],b[15], self.rb_id) for b in beer_tuples]
        
class BreweryTests(unittest.TestCase):
    
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()