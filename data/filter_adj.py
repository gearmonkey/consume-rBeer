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


def is_plural(a,b):
    """a really stupid pluralisation checker, english only
    returns true if b is standard form plural of a (or vis-a-versa) as defined by these rules:
        adds s or es
        subs y for ies
        subs f or fe for ves
    based on http://en.wikipedia.org/wiki/English_plural this should cover regular and near-regular plurals
    """
    if len(a) == len(b):
        #all [near-]regular plurals are longer, so:
        return False
    singular = min(a,b,key=len).lower()
    plural = max(a,b,key=len).lower()
    
    if singular + 's' == plural or singular + 'es' == plural:
        return True
    
    if singular[-1] == 'y':
        if singular[:-1] + 'ies' == plural:
            return True
            
    if singular[-1] == 'f' or singular[-2:] == 'fe':
        if singular[:-1] + 'ves' == plural or singular[:-2] + 'ves' == plural:
            return True
    
    #fail
    return False



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
    conn_out = sqlite3.connect(':memory:') #the db for new tags
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
        
        
        #Part of Speech filter
        #the gt 2 filter should really be in the IDF, but here also for now
        tokens_with_pos= [x[0] for x in nltk.pos_tag([tag for (tag,w) in tags]) \
                            if x[1] in ('NN', 'JJ') and x[0] not in name_tokens and len(x[0])>2] 
        tags = [tags[[a[0] for a in tags if len(a[0])].index(t)] for t in tokens_with_pos]
        
        #tag to tag plural filter
        for idx, (tag_a, w_a) in enumerate(tags):
            for tag_b_tuple in tags[idx:]:
                if is_plural(tag_a, tag_b_tuple[0]):
                    tags.pop(tags.index(tag_b_tuple))
        
        
        tagdb.execute('INSERT INTO filtered_tags (beer_id, tags) VALUES (?,?)', 
                      (beer_id, json.dumps(tags)))
        conn_out.commit()
    del(top_terms)
    with open(args.filtered_terms, 'w') as wh:
        filtered_tags = {}
        for beer_id, serialized_tags in conn_out.execute('SELECT beer_id, tags FROM filtered_tags'):
            filtered_tags[beer_id] = json.loads(serialized_tags)
        cPickle.dump(filtered_tags, wh)

            

if __name__ == "__main__":
    sys.exit(main())
