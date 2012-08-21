#!/usr/bin/env python
# encoding: utf-8
"""
sortidf.py

pulls in an idf model file, that looks like:

[number of documents]
[term1]:[document count]
[term2]:[document count]
  ...
[termN]:[document count]

and sorts the term list according to the document count, then writes it back to disk.

Usage:

> sortidf.py infile outfile

Created by Benjamin Fields on 2012-08-16.
Copyright (c) 2012 . All rights reserved.
"""

import sys
import codecs
from operator import itemgetter


help_message = '''
Usage:
> sortidf.py infile outfile
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg + '\n' + help_message


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        infile, outfile = argv[1:]
    except Exception, msg:
        raise Usage(msg)
    with codecs.open(infile, 'r', encoding='utf-8') as rh:
        term_counts = [(line.split(':')[0].strip(), int(line.split(':')[1].strip())) for line in rh.readlines()\
                            if len(line.split(':')) == 2]
        rh.seek(0)
        num_terms = int(rh.readline().strip())
    print 'read in', len(term_counts), 'terms from', num_terms, 'documents.'
    term_counts.sort(key=itemgetter(1), reverse=True)
    with codecs.open(outfile, 'wb', encoding='utf-8') as wh:
        wh.write(str(num_terms)+'\n')
        wh.write(u'\n'.join([u'{0}:{1}'.format(term, count) for term, count in term_counts]))
        wh.write('\n')

    



if __name__ == "__main__":
    sys.exit(main())
