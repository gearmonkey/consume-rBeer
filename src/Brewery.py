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


from Beer import beer

class Brewery:
	"""
	Basic manual instanciation can happen through __init__, but for standard 
	use via ratebeer scraping, creation of an instance should occur via the 
	static Brewery.parse
	"""
	regexes = {'name': re.compile('<h1>(.*?)</h1><span class=beerfoot>'),
			'type': re.compile('<br><font color="#666666">Type:(.*?)</font><br><br>'),
			'full_address': re.compile('<br><br><a href =".*?" target="new"><b>(.*?)<BR>(.*?)</b> <img'),
			'region' : re.compile('&gt; <a href="/beer/brewers/">Brewers</a> &gt;.*?&gt; <a href="(.*?)">(.*?)</a> &gt;'),
			'country': re.compile('&gt; <a href="/beer/brewers/">Brewers</a> &gt; (<a.*?>)?(.*?)(</a>)? &gt;'), 
			'url': re.compile('<br><small><A HREF="(?P<url>.*?)" TARGET=_blank>(?P=url)</A>'),
			'phone': re.compile('<IMG SRC="/images/phone.gif".*?>(.*?)<BR>'),
			'fb_url': re.compile('\|</font> Facebook: <a href="(.*?)" target="_blank">.*?</a><BR>'), 
			#the beer list regex will only pick up beers with all the stats, needs to be tweaked
			'beers': re.compile('<TR class=dataTableRowAlternate><TD width="65%" style="border-left: 0px solid #d7d7d7;"><font size=4>&nbsp;</font><A HREF="/beer/.*?/(?P<beerID>\d*?)/">(.*?)</A> &nbsp; </TD><TD valign=top>.*?</TD><TD align="right"><font color=#999999>(.*?)</font>&nbsp;&nbsp;</TD><TD><font color=#999999>&nbsp;&nbsp;(.*?)</font>&nbsp;&nbsp;</TD><TD align=center><b>(\d*?)</b>&nbsp;&nbsp;</TD><TD align=center><b>(\d*?)</b>&nbsp;&nbsp;</TD><TD align="right"><font color=#999999>(\d*?)</font>&nbsp;&nbsp;</TD>'), 	} 
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
		self.source_url = source_url
		self.rb_id = rb_id

	def parse(self, raw_page):
		"""
		uses the html string (should be text from a brewery page on 
		rate beer) raw_page to populate brewery attributes
		"""
		self.display_name = Brewery.regexes['name'].findall(raw_page)[0].strip()
		self.brewer_type = Brewery.regexes['type'].findall(raw_page)[0].strip()
		self.full_address = ','.join(Brewery.regexes['full_address'].findall(raw_page)[0])
		try:
			self.region = Brewery.regexes['region'].findall(raw_page)[0][-1].strip()
		except IndexError:
			#if no region, leave it as None
			logging.warning('Unable to parse a region for {0}'.format(self.display_name))
		self.country = Brewery.regexes['country'].findall(raw_page)[1].strip()
		self.url = Brewery.regexes['url'].findall(raw_page)[0].strip()
		self.phone = Brewery.regexes['phone'].findall(raw_page)[0].strip()
		try:
			self.fb_url = Brewery.regexes['fb_url'].findall(raw_page)[0]
		except IndexError:
			logging.warning('Unable to parse a facebook url for {0}'.format(self.display_name))
		self.beers = self._populate_beer_list(Brewery.regexes['beers'].findall(raw_page))
		
	def _populate_beer_list(self, beer_tuples):
		"""
		given a list of beer tuples of the form
			(stuff)
		create an instance of the Beer class for & with each beer_tuple
		append the resulting instance to self.beer
		for now just return the the list of tuples, since the beers class is a stub
		"""
		return beer_tuples
class BreweryTests(unittest.TestCase):
	
	def setUp(self):
		pass


if __name__ == '__main__':
	unittest.main()