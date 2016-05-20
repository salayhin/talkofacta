"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: feature extractors
The callables in this module extract features (e.g. words and noun_phrases) from text.

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
from textblob import TextBlob
from unidecode import unidecode
from textblob.np_extractors import ConllExtractor
from collections import Counter
import requests
import json


def words(txt):
    return Counter(TextBlob(unidecode(txt)).words.lower().lemmatize())


class NounPhraseExtractor(object):
    """
    Usage:
        >>>extr = NounPhraseExtractor()
        >>>extr("Hello Mister President")
        >>>['mister president']
    """
    def __init__(self):
        self.extractor = ConllExtractor()
        
    def __call__(self, txt):
        return list(TextBlob(unidecode(txt), np_extractor=self.extractor).noun_phrases)

noun_phrases = NounPhraseExtractor()

def dbpedia_entities(txt):
    url = 'http://spotlight.dbpedia.org/rest/annotate'
    payload = {'text': txt, 'confidence': 0.2, 'support:': 20}
    headers = {'Accept': 'application/json'}
    r = requests.post(url, data=payload, headers=headers)
    return json.loads(r.text)