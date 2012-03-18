import time
import sqlite3
import logging

import Beer

NUM_BEERS = 168719 # total number of beers as of 13-03-2012 @2200GMT
REPORT_EVERY = 1000

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

conn = sqlite3.connect('rbeer.db')
c = conn.cursor()

c.execute('''create table beer
(id integer primary key, brewery integer, name text, abv real, mean_score real,
weighted_score real,overall_percentile real, style_percentile real,
total_ratings integer, style_id integer)''')
c.execute('''create table review
(id integer primary key autoincrement, beer_uid integer NOT NULL, user_uid integer, 
brewery_uid integer, topline_score integer, aroma_score integer, apperance_score integer,
taste_score integer, palete_score integer, overall_score integer, location text, 
user_location text, date integer, comment text)''')
conn.commit()

for beer_id in [138065]: #xrange(NUM_BEERs):
    logging.debug('fetching beer {0}'.format(beer_id))
    if beer_id%REPORT_EVERY == 0:
        logging.info('scrape is {0}% done.'.format(100*(float(beer_id)/NUM_BEERS)))
    a_beer = Beer.Beer(beer_id)
    a_beer.page = a_beer.fetch_beer_page()
    a_beer.parse_metadata(a_beer.page)
    c.execute('''insert into beer values (?,?,?,?,?,?,?,?,?,?)''', [a_beer.uid,
                                                                    a_beer.name.decode('latin-1'),
                                                                    a_beer.abv, 
                                                                    a_beer.mean_score,
                                                                    a_beer.weighted_score,
                                                                    a_beer.overall_percentile,
                                                                    a_beer.style_percentile,
                                                                    a_beer.total_ratings,
                                                                    a_beer.brewery_id,
                                                                    a_beer.style_id])
    a_beer.scrape_user_comment_list(a_beer.page)
    for review in a_beer.reviews:
        c.execute('''insert into review (beer_uid, user_uid, brewery_uid, topline_score, aroma_score, 
        apperance_score, taste_score, palete_score, overall_score, user_location, date, comment) values     
        (?,?,?,?,?,?,?,?,?,?,?,?)''',[review.beer_uid,
                                        review.user_uid, 
                                        review.brewery_uid,
                                        review.topline_score, 
                                        review.aroma_score,
                                        review.apperance_score, 
                                        review.taste_score, 
                                        review.palete_score, 
                                        review.overall_score, 
                                        review.user_loc.decode('latin-1'), 
                                        int(time.mktime(review.date.timetuple())),
                                        review.comment.decode('latin-1')])
    conn.commit()
    