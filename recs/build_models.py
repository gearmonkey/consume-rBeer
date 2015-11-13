import logging
import sys
import cPickle
import sqlite3
import time

import spacy.en
from gensim import corpora, models, similarities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main(argv=sys.argv):
    """docstring for main"""
    try:
        corpus_file, tfidf_file, lda_file = argv[1], argv[2], argv[3]
    except IndexError:
        corpus_file = 'corpus.pickle'
        tfidf_file = 'tfidf.pickle'
        lda_file = 'lda.pickle'
    #insure things are writeable
    corpus_handle = open(corpus_file, 'w')
    corpus_handle.close()

    conn = sqlite3.connect('../data/rbeer.db')
    cur = conn.cursor()

    print time.asctime(), "loading beers"
    cur.execute('select id from beer')
    beers = cur.fetchall()
    corpus = []

    print time.asctime(), "loading dictionary"
    beerwords = corpora.Dictionary.load('beerwords.dict')
    print time.asctime(), "loading spacy models"
    nlp = spacy.en.English()
    print time.asctime(), "load corpus and build dictionary"
    idx = 0
    for (beer_id,) in beers:
        cur.execute('select comment from review where beer_uid = ?', (beer_id,))
        all_comments = u''.join(map(lambda x:x[0], cur.fetchall()))
        tokens = nlp(all_comments)
        #what if any token filtering?
        #currently just ditch case and ignore small words
        cleaned_tokens = filter(lambda x:len(x)>2, map(lambda x:x.text.strip().lower(), tokens))
        corpus += [beerwords.doc2bow(cleaned_tokens)]
        idx += 1
        if idx%500 == 0:
            print len(corpus), "documents in corpus"
            print time.asctime(), "preprocessed", idx, "docs. ", 100 - 100*(idx/float(len(beers))), "perc remain"
            # with open(corpus_file, 'w') as wh:
            #     cPickle.dump(corpus, wh)

    #save the corpus and the dictionary
    # beerwords.save('beerwords.dict')
    with open(corpus_file, 'w') as wh:
        cPickle.dump(corpus, wh)

    tfidf = models.TfidfModel(corpus, dictionary=beerwords)
    tfidf.save(tfidf_file)
    print "tfidf:"
    print tfidf

    lda = models.LdaModel(corpus, id2word=beerwords, num_topics=200)
    lda.save(lda_file)
    print "lda:"
    print lda

if __name__ == '__main__':
    main()