#similarity
import sqlite3
import spacy.en

from gensim import corpora, models, similarities

beerwords = corpora.Dictionary.load('beerwords.dict')
nlp = spacy.en.English

conn = sqlite3.connect('../data/rbeer.db')
cur = conn.cursor()

for (beer_id,) in beers:
    cur.execute('select comment from review where beer_uid = ?', (beer_id,))
    all_comments = u''.join(map(lambda x:x[0], cur.fetchall()))
    tokens = nlp(all_comments)
    cleaned_tokens = filter(lambda x:len(x)>2, map(lambda x:x.text.strip().lower(), tokens))
    corpus += beerwords.doc2bow(cleaned_tokens)

beer_model =  models.LdaModel(corpus, id2word=beerwords, numtopics=200)

index = similarities.MatrixSimilarity(beer_model[corpus])

kernel_estout = beer_model[corpus[83584]]
like_kernel = sorted(list(enumerate(index[kernel_estout])), key = lambda x:x[1], reverse=True)

cur.execute("select rbid from brewery where region LIKE '%new york%'")
ny_brew = zip(*cur.fetchall())[0]

cur.execute('select id, name, brewery from beer')
beer_mapping = dict(list(enumerate(cur.fetchall())))
hits = 0

for corpus_id, score in like_kernel:
    if beer_mapping[corpus_id][3] > 4 and beer_mapping[corpus_id][2] in ma_brew:
        print beer_mapping[corpus_id][1], beer_mapping[corpus_id][0], score
        hits += 1
        if hits > 5:
            break

