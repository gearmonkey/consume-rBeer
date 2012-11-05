#!/usr/bin/env python
# encoding: utf-8
"""
exportdb2es.py

Created by Benjamin Fields on 2012-10-07.
Copyright (c) 2012 . All rights reserved.
"""

import sys
import argparse
import sqlite3
import cPickle
import simplejson as json

import nltk, nltk.tokenize




class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):

    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description='Populates the adjective only top terms, from the top terms column, for every beer')
    parser.add_argument('tfidf_path', help='pickle of tfidf data')
    parser.add_argument('database', help='a sqlite3 db of rbeer data')
    parser.add_argument('filtered_terms', help='pickled output of filtered tfidf data')
    
    args = parser.parse_args()

    conn = sqlite3.connect(args.database)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    conn_out = sqlite3.connect('temp.db') #the db for new tags
    tagdb = conn_out.cursor()
    tagdb.execute('CREATE TABLE filtered_tags (beer_id integer primary key, tags text)')
    
    c.execute('SELECT count(*) from beer')
    to_insert = c.fetchone()['count(*)']
    print to_insert, 'beers from',args.database ,'will be filtered, filtered terms saved in', args.filtered_terms

    c.execute('SELECT * from beer')
    with open(args.tfidf_path) as rh:
        top_terms = cPickle.load(rh)

    for idx, (beer_id, tags) in enumerate(top_terms.items()):
        c.execute('SELECT name FROM beer WHERE id=?',(beer_id,))
        try:
            name = c.fetchone()[0]
        except:
            print 'no name found for beer id {0}, continueing...'.format(beer_id)
            name = ''
        name_tokens = [t.lower() for t in nltk.tokenize.word_tokenize(name.replace('.', ''))]

        tokens_with_pos= [x[0] for x in nltk.pos_tag([tag for (tag,w) in tags]) \
                            if x[1] in ('NN', 'JJ') and x[0] not in name_tokens]
        filtered_tags = [tags[[a[0] for a in tags].index(t)] for t in tokens_with_pos]
        tagdb.execute('INSERT INTO filtered_tags (beer_id, tags) VALUES (?,?)', 
                      (beer_id, json.dumps(filtered_tags)))
        conn_out.commit()
    del(top_terms)
    with open(args.filtered_terms, 'w') as wh:
        filtered_tags = {}
        for beer_id, serialized_tags in conn_out.execute('SELECT beer_id, tags FROM filtered_tags'):
            filtered_tags[beer_id] = json.loads(serialized_tags)
        cPickle.dump(filtered_tags, wh)

            

if __name__ == "__main__":
    sys.exit(main())
