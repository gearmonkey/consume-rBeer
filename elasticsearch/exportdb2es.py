#!/usr/bin/env python
# encoding: utf-8
"""
exportdb2es.py

Created by Benjamin Fields on 2012-10-07.
Copyright (c) 2012 . All rights reserved.
"""

import sys
import argparse




class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
        parser = argparse.ArgumentParser(description='Export an sqlite3 rbeer db to elasticsearch.')
        parser.add_argument('-t', '--tfidf', dest='tfidf_path', help='pickle of tfidf data')
        parser.add_argument('database', help='a sqlite3 db of rbeer data')
        parser.add_argument('es-host', help='URL of elastic search host')
        args = parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
