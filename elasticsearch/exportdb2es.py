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

import pyelasticsearch




class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):

    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description='Export an sqlite3 rbeer db to elasticsearch.')
    parser.add_argument('-t', '--tfidf', dest='tfidf_path', help='pickle of tfidf data')
    parser.add_argument('database', help='a sqlite3 db of rbeer data')
    parser.add_argument('es_host', help='URL of elastic search host')
    args = parser.parse_args()

    conn = sqlite3.connect(args.database)
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    c = conn.cursor()
    c.execute('SELECT count(*) from beer')
    to_insert = c.fetchone()['count(*)']
    es_index = args.es_host.split('/')[-1]
    print to_insert, 'beers from',args.database ,'will be inserted to the elasticsearch hosted at', args.es_host, "using the index", es_index
    if args.tfidf_path:
        print 'top terms will be included from', args.tfidf_path
    else:
        print 'no top terms will be used'
    c.execute('SELECT * from beer')
    if args.tfidf_path:
        with open(args.tfidf_path) as rh:
            top_terms = cPickle.load(rh)
    else:
        top_terms = {}
    es_client = pyelasticsearch.ElasticSearch(args.es_host)
    bulk_beers = []
    for idx, row in enumerate(c.fetchall()):
        this_beer = dict(row)
        rbeer_id = this_beer.pop('id')
        this_beer['ratebeer_id'] = rbeer_id
        this_beer['name'] = unicode(this_beer['name'], 'utf-8', 'replace')
        if this_beer.has_key('clean_name') and this_beer['clean_name']!=None:
            this_beer['clean_name'] = unicode(this_beer['clean_name'], 'utf-8', 'replace')
        this_beer['brewery_name'] = ''
        c.execute('SELECT rbid, name, url FROM brewery WHERE rbid={0}'.format(row['brewery']))
        brewery_metadata = c.fetchone()
        if brewery_metadata!=None:
            #the encoding is a bit fucked...
            this_beer['brewery_name'] = unicode(brewery_metadata['name'], 'utf-8', 'replace')
            this_beer['brewery_url'] = unicode(brewery_metadata['url'], 'utf-8', 'replace')
        try:
            this_beer['topterms'] = [t for t in top_terms[int(row['id'])] if len(t[0]) > 2 and '@' not in t[0]]
        except KeyError:
            print 'no top terms for', row['name']
            this_beer['topterms'] = []
        bulk_beers.append(this_beer)
        if idx%500 == 0:
            es_client.bulk_index(es_index, 'beer',  bulk_beers, 'ratebeer_id')
            print 'uploaded', idx/float(to_insert), 'percent of the beers'
            bulk_beers = []
    es_client.bulk_index(es_index, 'beer', bulk_beers, 'ratebeer_id', refresh=True)
    print 'uploaded', idx/float(to_insert), 'percent of the beers'
    print 'finished uploads, rebuilding index'
        
            
        
    
    
    
    
    
    




if __name__ == "__main__":
    sys.exit(main())
