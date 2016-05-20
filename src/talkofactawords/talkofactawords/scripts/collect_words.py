"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: collect_words
Compute the set of words that will be considered for extracting significant ones.

Inputs word features extracted using ``compute_features words`` and stored in
<zodb_dir>. Selects a set of words that is common for five largest countries (by speech counts).
Subtracts from that stopwords for numerous languages.

Writes output into ZODB variable root.all_words as a python set object.

   Usage: collect_words [-h]

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
from sqlalchemy import func, desc
from docopt import docopt
from unidecode import unidecode
import transaction
import nltk
from talkofactadb.model import Speech, open_db
from talkofactadb.config import get_config
from talkofactawords.zodb import open_zodb
from clint.textui import progress

def main():
    args = docopt(__doc__)
    c = get_config()
    session = open_db()
    zodb_root = open_zodb(read_only=True)
    ids = session.query(Speech.id).all()
    all_words = set()
    for (id,) in progress.bar(ids, label="Progress: ", every=100):
        all_words = all_words.union(zodb_root.features['words'][id].keys())

    print "Word set size: ", len(all_words)

    #print "Subtracting stopwords..."
    #nltk.download('stopwords')
    #langs = ['english', 'spanish']
    #all_stopwords = reduce(lambda x, y: x | y, [set(nltk.corpus.stopwords.words(lng)) for lng in langs])
    #all_stopwords = set(map(unidecode, all_stopwords))
    #all_words = all_words - all_stopwords
    #print "Resulting word set size: ", len(all_words)

    print "Saving..."
    zodb_root = open_zodb()
    zodb_root.all_words = all_words
    transaction.commit()
    print "Done"