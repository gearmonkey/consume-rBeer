#!/usr/bin/env python
# encoding: utf-8
"""
getBreweries.py

Populate Brewery metadata for all Beers in the passed database.


Created by Benjamin Fields on 2013-02-11.
Copyright (c) 2013 . Some rights reserved.
"""

import sys
import os
import time

import simplejson as json
import sqlite3
from Brewery import Brewery

def escape_q(aStr):
    return str(aStr).replace('"', "'")


def main():
    db_filename = sys.argv[1]
    conn = sqlite3.connect(db_filename)
    curs = conn.cursor()
    curs.execute("SELECT distinct(brewery) from beer")
    
    ins_stmt = """INSERT OR REPLACE INTO brewery (rbid, name, url, country, region, full_address, phone, fb_url, beers) VALUES (?,?,?,?,?,?,?,?,?)"""

    breweries = curs.fetchall()
    for i, (brewery,) in enumerate(breweries):
        #skip some
        if brewery < 0:
            continue
        try:
            this_brewery = Brewery(rb_id = brewery)
            this_brewery.parse()
        except:
            print "cannot parse the brewery with the ID", brewery
            continue
        # print 'about to insert:', ins_stmt,(brewery,this_brewery.display_name,
        #                                     this_brewery.url,this_brewery.country,
        #                                     this_brewery.region,this_brewery.full_address,
        #                                     this_brewery.phone,this_brewery.fb_url,
        #                                     json.dumps(this_brewery.beers))
        curs.execute(ins_stmt,(brewery,this_brewery.display_name,this_brewery.url,
                               this_brewery.country,this_brewery.region,this_brewery.full_address,
                               this_brewery.phone,this_brewery.fb_url,json.dumps(this_brewery.beers, encoding=unicode)))
        time.sleep(0.5)
        if i%100==0:
            print time.asctime(), 'finished with', i, 'breweries'
            conn.commit()
        

if __name__ == '__main__':
    main()

