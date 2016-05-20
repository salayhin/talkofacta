# -*- coding: UTF-8 -*-
"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: Visualization webapp
Views.

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
from flask import render_template, request, jsonify
from .main import app
from .model import db, ByHansard, ByMonth, BySpeaker
from sqlalchemy import *
from math import log

MAX_WORDS = 150

# ----------------------------------- Logic ------------------------------------- #
class WordSizer(object):
    '''Given a list of words (each represented as a dict with 'odds' field representing the odds score of the word),
       computes suitable wordcloud sizes, adding the 'size' field to each object)'''

    tol = 1e-10
    MIN_SIZE = 12
    MAX_SIZE = 70

    def __call__(self, words):
        if len(words) == 0:
            return words
        sizes = [log(max(w['odds'], self.tol)) for w in words]
        max_size = max(sizes)
        min_size = min(sizes)
        if (max_size == min_size):
            max_size = min_size + 1
        a = (self.MAX_SIZE - self.MIN_SIZE)/(max_size - min_size)
        b = self.MIN_SIZE - a*min_size
        sizes = [a*s + b  for s in sizes]
        for i, w in enumerate(words):
            w['size'] = sizes[i]
        return words

wsizer = WordSizer()

# ----------------------------------- Views ------------------------------------- #
@app.route('/')
def index():
    return render_template('index.html')

# ------------------------------ By Hansard ------------------------------ #
@app.route('/by_hansard')
def by_hansard():
    hansards = [c for (c,) in db.session.query(distinct(ByHansard.foreground_group_name)).order_by(ByHansard.foreground_group_name)]
    return render_template('by_hansard.html', hansards=hansards)

@app.route('/words/by_hansard/<code>')
def words_by_hansard(code):
    assert len(code) <= 8 and code.startswith('ACTA')
    unique = int(request.args.get('unique', 0))
    if int(unique) != 0:
        results = db.session.query(ByHansard).filter(ByHansard.foreground_group_name == code).\
            filter(text("word not in (select word from words_byhansard where foreground_group_name != '%s')" % code)).order_by(ByHansard.pval, desc(ByHansard.odds)).limit(MAX_WORDS)
    else:
        results = db.session.query(ByHansard).filter(ByHansard.foreground_group_name == code).order_by(ByHansard.pval, desc(ByHansard.odds)).limit(MAX_WORDS)
    words = [{'text': o.word, 'odds': min(float(o.odds), 100), 'pval': float(o.pval)} for o in results]
    return jsonify(words = wsizer(words))

@app.route('/wordstats/by_hansard/<word>')
def wordstats_by_hansard(word):
    hansards = [c[0] for c in db.session.query(distinct(ByHansard.foreground_group_name)).order_by(ByHansard.foreground_group_name)]
    val = {c.foreground_group_name: min(float(c.odds), 100) for c in db.session.query(ByHansard).filter(ByHansard.word == word)}
    data = [{"hansard": cn, "value": val.get(cn, None)} for cn in hansards]
    return jsonify(data=data)

# ------------------------------ By Month ------------------------------ #
@app.route('/by_month')
def by_month():
    return render_template('by_month.html', min_year=2013, max_year=2015)

@app.route('/words/by_month/<code>')
def words_by_month(code):
    results = db.session.query(ByMonth).filter(ByMonth.foreground_group_name == code).order_by(ByMonth.pval, desc(ByMonth.odds)).limit(MAX_WORDS)
    words = [{'text': o.word, 'odds': min(float(o.odds), 100), 'pval': float(o.pval)} for o in results]
    return jsonify(words = wsizer(words))

@app.route('/wordstats/by_month/<word>')
def wordstats_by_month(word):
    months = [c for (c,) in db.session.query(distinct(ByMonth.foreground_group_name)).order_by(ByMonth.foreground_group_name)]
    val = {c.foreground_group_name: min(float(c.odds), 100) for c in db.session.query(ByMonth).filter(ByMonth.word == word)}
    data = [{"month": m, "value": val.get(m, None)} for m in months]
    return jsonify(data=data)





# ------------------------------------ Error handlers ---------------------------------------- #
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
