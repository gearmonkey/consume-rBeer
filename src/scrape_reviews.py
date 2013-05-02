import time
import sqlite3
import logging

import Beer

NUM_BEERS = 211699 # total number of beers as of 13-03-2012 @2200GMT
REPORT_EVERY = 1000

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

conn = sqlite3.connect('rbeer.db')
c = conn.cursor()

# ###DB schema###
# c.execute('''CREATE TABLE beer
# (id integer primary key, brewery integer, name text, abv real, mean_score real,
# weighted_score real,overall_percentile real, style_percentile real,
# total_ratings integer, style_id integer, beeradvocate_id char96, beeradvocate_mean_score float, 
# untapped_id int, untappd_mean_score float, clean_name)''')
# c.execute('''create table review
# (id integer primary key autoincrement, beer_uid integer NOT NULL, user_uid integer, 
# brewery_uid integer, topline_score integer, aroma_score integer, apperance_score integer,
# taste_score integer, palete_score integer, overall_score integer, location text, 
# user_location text, date integer, comment text)''')
# conn.commit()

#if not populating a new db, let's only get things we don't have in the database yet
c.execute('SELECT DISTINCT id from beer')
visited_beers = [b for (b,) in c.fetchall()]


for beer_id in (b for b in xrange(1, NUM_BEERS) if not b in visited_beers): #range of beers
# for beer_id in (198874, 199216, 190724, 204737): #some specific ones
    logging.debug('fetching beer {0}'.format(beer_id))
    if beer_id%REPORT_EVERY == 0:
        logging.info('scrape is {0}% done.'.format(100*(float(beer_id)/NUM_BEERS)))
    a_beer = Beer.Beer(beer_id)
    try:
        a_beer.page = a_beer.fetch_beer_page()
        a_beer.parse_metadata(a_beer.page)
    except IndexError:
        logging.error('beer {0} doesn\'t work right, moving on'.format(beer_id))
        continue
    c.execute('''INSERT OR REPLACE INTO beer (id, brewery, name, abv, mean_score, weighted_score, overall_percentile, style_percentile,total_ratings, style_id) VALUES (?,?,?,?,?,?,?,?,?,?)''', [a_beer.uid,
                                                                    a_beer.brewery_id,
                                                                    a_beer.name.decode('latin-1'),
                                                                    a_beer.abv, 
                                                                    a_beer.mean_score,
                                                                    a_beer.weighted_score,
                                                                    a_beer.overall_percentile,
                                                                    a_beer.style_percentile,
                                                                    a_beer.total_ratings,
                                                                    a_beer.style_id,])
    a_beer.scrape_user_comment_list(a_beer.page)
    for review in a_beer.reviews:
        c.execute('''INSERT OR REPLACE into review (beer_uid, user_uid, brewery_uid, topline_score, aroma_score, 
        apperance_score, taste_score, palete_score, overall_score, user_location, date, comment) VALUES     
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
    