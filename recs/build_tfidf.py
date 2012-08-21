import sqlite3
import logging
import sys
import StringIO
import cPickle

from tfidf import TfIdf



conn = sqlite3.connect('../rbeer.db')
args = sys.argv
if "--in-mem" in args or "-m" in args:
    #pop the arg
    if "--in-mem" in args:
        args.pop(args.index("--in-mem"))
    if "-m" in args:
        args.pop(args.index("-m"))
    print "shifting db to memory"
    # Read database to tempfile
    tempfile = StringIO.StringIO()
    for line in conn.iterdump():
        tempfile.write(u'{0}\n'.format(line))
    conn.close()
    tempfile.seek(0)
    
    # Create a database in memory and import from tempfile
    conn = sqlite3.connect(":memory:")
    conn.cursor().executescript(tempfile.read())
    conn.commit()
    conn.row_factory = sqlite3.Row
    tempfile.close()
    
c = conn.cursor()
    
try:
    save_file = int(sys.argv[1])
except IndexError:
    save_file = 'pickled_tfidf.pickle'

print "saving to ", save_file

with open(save_file, 'w') as wh:
    wh.write('0\n')

comment_model = TfIdf(corpus_filename="idf_model.txt", stopword_filename="curated_stopwords.txt", 
                        DEFAULT_IDF=None)

#find the number of beers for progress indication
c.execute("SELECT id from beer")
total_beers = len(list(c.fetchall()))
print "calculating tfidf of ", total_beers, "beers."

c.execute("SELECT id, brewery FROM beer")
idx = 0 #don't want to unwrap the generator so we'll idex this way
worked = 0
top_100 = {}
for beer_id, name in c.fetchall():
    if idx%1000 == 0:
        print """*-*-*-* Finished {0}% of the processing.""".format(float(idx)/total_beers)
        with open(save_file, 'w') as wh:
            cPickle.dump(top_100, wh)
    idx += 1
    try:
        int(beer_id)
    except:
        print "the beer", name, "has this id", beer_id, "which doesn't look like an int..."
        continue
    try:
        c.execute("SELECT comment FROM review WHERE beer_uid = {0}".format(beer_id))
    except Exception, err:
        print "the beer", name, "has this id", beer_id, "and is giving this error:", err
        continue
    comments = ''
    for comment, in c.fetchall():
        comments += comment
    top_100[int(beer_id)] = comment_model.get_doc_keywords(comments)
    print "dealt with", name
    worked += 1
print "sucessfully dealt with", worked, "beers."
print "finished, storing tfidfs..."
with open(save_file, 'w') as wh:
    cPickle.dump(top_100, wh)

    