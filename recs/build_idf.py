import sqlite3
import logging
import sys
import StringIO

from tfidf import TfIdf

conn = sqlite3.connect('../data/rbeer.db')
args = sys.argv

if "-s" in args:
    args.pop(args.index("-s"))
    print "Only correctly spelled english words to be used in IDF"
    import re
    from nltk.corpus import wordnet
    class CleanedTfIdf(TfIdf):
        """overrides the default TfIdf class to only produces correctly spelled english language words.
        instanciated here to prevent nltk dependancy unless needed"""
        def get_tokens(self, str):
            """overrides the default tokenizer to only used english language correctly spelled words
            Break a string into tokens, preserving URL tags as an entire token.
            This implementation does not preserve case.  
            """
            raw_tokens = re.findall(r"<a.*?/a>|<[^\>]*>|[\w'@#]+", str.lower())
            return [t for t in raw_tokens if wordnet.synsets(t)]
    comment_model = CleanedTfIdf(stopword_filename="stopwords.txt", 
                            DEFAULT_IDF=None)
else:
    comment_model = TfIdf(stopword_filename="stopwords.txt", 
                            DEFAULT_IDF=None)
    
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
    bottom_idx = int(sys.argv[1])
    print "using", bottom_idx, "as start point"
except IndexError:
    bottom_idx = None
try:
    top_idx = int(sys.argv[2])
    print "using", top_idx, "as end point"
except IndexError:
    top_idx = None

if bottom_idx or top_idx:
    suffix = '_'
    if bottom_idx:
        suffix += str(bottom_idx)
    else:
        suffix += "0"
    if top_idx:
        suffix += "-"+str(top_idx)
else:
    suffix = ""
idf_model_save_path = "idf_model{0}.txt".format(suffix)
inferred_stopwords_path = "inferred_stopwords{0}.txt".format(suffix)
#find the number of beers for progress indication
c.execute("SELECT id from beer")
total_beers = len(list(c.fetchall()))
print "idf will be built from the reviews of ", total_beers, "beers."

c.execute("SELECT id, name FROM beer")
idx = 0 #don't want to unwrap the generator so we'll idex this way
worked = 0
for beer_id, name in c.fetchall():
    if bottom_idx!=None and idx<bottom_idx:
        idx+=1
        continue
    if top_idx!=None and idx>top_idx:
        break
    if idx%1000 == 0:
        print """*-*-*-* Finished {0}% of the processing.""".format(float(idx)/total_beers)
        comment_model.save_corpus_to_file(idf_model_save_path,inferred_stopwords_path)
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
    comment_model.add_input_document(comments)
    print "dealt with", name
    worked += 1
print "sucessfully dealt with", worked, "beers."
print "finished, storing model..."
comment_model.save_corpus_to_file(idf_model_save_path,inferred_stopwords_path)

    