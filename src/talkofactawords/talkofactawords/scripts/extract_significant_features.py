"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: extract_significant_features script
The script performs group-specific feature extraction.
The features must be precomputed in ZODB using the compute_features script.
The database location is specified by <zodb_dir> config variable.
Script runs in parallel using <num_cores> cores and stores the results into a relational
database specified by <resultsdb_url>.

   Usage: extract_significant_features [-h] <feature_name> <experimentset_name>

   where
       <feature_name>  - is the name of the precomputed feature vector
                         (as given to compute_features, i.e. "words" or "noun_phrases").
       <experimentset_name> - is the name of the "experiment set", currently supported are:
                     by_hansard
                     by_month
                     by_speaker

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
import os, signal, cPickle
from docopt import docopt
from multiprocessing import Pool
from sqlalchemy import distinct, func
from collections import Counter
import BTrees
import transaction
from talkofactadb.config import get_config
from talkofactawords.zodb import open_zodb
from talkofactadb.model import open_db
from talkofactadb.model import Speech
from talkofactawords.model import create_db, ByHansard, ByMonth, BySpeaker
from clint.textui import progress
import datetime
from dateutil.relativedelta import relativedelta

from scipy.stats import fisher_exact

def init_worker():  # Ignore keyboard interrupts (will catch those in parent)
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class ExperimentSet(object):
    '''
    Class describing an "experiment set" for extracting significant features. An example of an "experiment set" is
    a "by_country" set, where we extract a set of significant words for each country by comparing each country's
    word usage with other countries.

    For purposes of parallelization, the experiment set is run in several steps:
       - First we precompute vector sums for a number of "foreground groups" (e.g. in by_country each foreground group is a set of
         speeches made by one country). This is run in parallel. We save results into a "cache" dictionary indexed by group name.
       - Then we compute (one or more) "background groups" (e.g. in by_country there is a single background group,
         which is the sum of all words). This can make use of the "cache" dictionary and results are also saved there.
       - The computed group sums are written to ZODB for future reuse under group_sums[feature_name][group_name]
       - Finally, we define an "experiment set" as a list of foreground/background groups.
         We run fisher test-based feature selection on each combination. This also runs in parallel.
         The results are saved in an SQL database for use in a webapp.
    The actual implementation of list_foreground_groups, list_background_groups, list_experiments should be done in subclasses.
    '''
    def __init__(self, pval_cutoff=0.01, feature_name='words'):
        self.pval_cutoff = pval_cutoff
        self.feature_name = feature_name
        self.config = get_config()

    def __getstate__(self):
        '''Data sent to the subprocesses.'''
        return {'pval_cutoff': self.pval_cutoff, 'feature_name': self.feature_name, 'config': self.config}

    def list_foreground_groups(self):
        'Lists "foreground group" codes'
        return []

    def list_background_groups(self):
        'Lists "background group" codes'
        return []

    def list_experiments(self):
        'Returns list of pairs of group ids'
        return []

    def compute_foreground_group_sum(self, group_name):
        'Given "foreground group" id return a sum_vector for that group. Runs on worker nodes.'
        return None

    def compute_background_group_sum(self, group_name, cache):
        """Given "background group" id return a "sum vector" for that group.
           This method may use previously precomputed "foreground group" vectors."""
        return None

    def extract_features(self, foreground_group_name, background_group_name):
        """Extract overrepresented words for a given foreground/background group. Runs on worker nodes.
           Uses zodb.group_sums[self.feature_name] data precomputed in previous steps."""
        z = open_zodb(self.config, read_only=True)
        fg_counts = z.group_sums[self.feature_name][foreground_group_name]
        bg_counts = z.group_sums[self.feature_name][background_group_name]
        total_fg_count = sum(fg_counts.values())
        total_bg_count = sum(bg_counts.values())

        result = []
        cutoff = 0.01/max(1, len(fg_counts))

        for w in fg_counts:
            contingency = [[fg_counts[w],                  bg_counts[w] - fg_counts[w]],
                           [total_fg_count - fg_counts[w], total_bg_count - total_fg_count - bg_counts[w] + fg_counts[w]]]
            odds, pval = fisher_exact(contingency, alternative='greater')
            if pval < cutoff:
              result.append((w, odds, pval))
        return result

    def result_table_class(self):
        '''Returns a SQLAlchemy ORM class that is used to store results.'''
        return None


class WordByHansard(ExperimentSet):
    '''Finds the most discriminative words for each hansard vs all other hansards.'''

    def __init__(self, pval_cutoff=0.01, feature_name='words'):
        super(WordByHansard, self).__init__(pval_cutoff, feature_name)

        print "Loading db..."
        session = open_db()
        self.all_hansards = [r[0] for r in session.query(distinct(Speech.hansard))]

    def list_foreground_groups(self):
        return self.all_hansards

    def list_background_groups(self):
        return ['*']

    def list_experiments(self):
        return [(c, '*') for c in self.all_hansards]

    def compute_foreground_group_sum(self, group_name):
        session = open_db(self.config.db_url)
        zodb = open_zodb(self.config, read_only=True)
        result = Counter()
        wordset = zodb.all_words
        for (id,) in session.query(Speech.id).filter(Speech.hansard == group_name):
            v = zodb.features[self.feature_name][id]
            for w in v:
                if w in wordset:
                    result[w] += v[w]
        return result

    def compute_background_group_sum(self, group_name, cache):
        assert group_name == '*'
        return reduce(lambda x, y: x+y, cache.values())

    def result_table_class(self):
        return ByHansard


class WordBySpeaker(ExperimentSet):
    '''Finds the most discriminative words for each hansard vs all other hansards.'''

    def __init__(self, pval_cutoff=0.01, feature_name='words'):
        super(WordBySpeaker, self).__init__(pval_cutoff, feature_name)

        print "Loading db..."
        session = open_db()
        self.all_speakers = [r[0] for r in session.query(distinct(Speech.speaker_uri))]

    def list_foreground_groups(self):
        return self.all_speakers

    def list_background_groups(self):
        return ['*']

    def list_experiments(self):
        return [(c, '*') for c in self.all_speakers]

    def compute_foreground_group_sum(self, group_name):
        session = open_db(self.config.db_url)
        zodb = open_zodb(self.config, read_only=True)
        result = Counter()
        wordset = zodb.all_words
        for (id,) in session.query(Speech.id).filter(Speech.speaker_uri == group_name):
            v = zodb.features[self.feature_name][id]
            for w in v:
                if w in wordset:
                    result[w] += v[w]
        return result

    def compute_background_group_sum(self, group_name, cache):
        assert group_name == '*'
        return reduce(lambda x, y: x+y, cache.values())

    def result_table_class(self):
        return BySpeaker


class WordByMonth(ExperimentSet):
    '''Finds the most discriminative words for each month.'''

    def __init__(self, pval_cutoff=0.01, feature_name='words'):
        super(WordByMonth, self).__init__(pval_cutoff, feature_name)

        print "Loading db..."
        s = open_db()
        min_date = s.query(func.min(Speech.date)).first()[0]
        max_date = s.query(func.max(Speech.date)).first()[0]
        min_month = datetime.date(min_date.year, min_date.month, 1)
        max_month = datetime.date(max_date.year, max_date.month, 1)
        all_months = []
        m = min_month
        while m <= max_month:
            all_months.append("%04d-%02d" % (m.year, m.month))
            m = m + relativedelta(months=1)
        self.all_months = all_months

    def list_foreground_groups(self):
        return self.all_months

    def list_background_groups(self):
        return ['*']

    def list_experiments(self):
        return [(c, '*') for c in self.all_months]

    def compute_foreground_group_sum(self, group_name):
        session = open_db(self.config.db_url)
        zodb = open_zodb(self.config, read_only=True)
        result = Counter()
        wordset = zodb.all_words
        y, m = map(int, group_name.split('-'))
        dmin = datetime.date(y,m,1)
        dmax = dmin + relativedelta(months=1)
        for (id,) in session.query(Speech.id).filter(Speech.date >= dmin).filter(Speech.date < dmax):
            v = zodb.features[self.feature_name][id]
            for w in v:
                if w in wordset:
                    result[w] += v[w]
        return result

    def compute_background_group_sum(self, group_name, cache):
        assert group_name == '*'
        return reduce(lambda x, y: x+y, cache.values())

    def result_table_class(self):
        return ByMonth


class ComputeForegroundGroupSumCallable(object):
    """We need to wrap our experiment_set into this object for passing into worker nodes for two reasons:
       - We can't pass a method, but we can pass a callable class for pickling reasons.
       - The compute_foreground_group_sum method returns a vector, but we would like to get (group_name, vector) for reasons of
         progress tracking
    """
    def __init__(self, experiment_set):
        self.experiment_set = experiment_set
    def __call__(self, group_name):
        res = self.experiment_set.compute_foreground_group_sum(group_name)
        return (group_name, res)


class ComputeOverrepresentedWordsCallable(object):
    """A wrapper over experiment_set which invokes extract_features.
    """
    def __init__(self, experiment_set):
        self.experiment_set = experiment_set
    def __call__(self, experiment):
        fg, bg = experiment
        results = self.experiment_set.extract_features(fg, bg)
        return (fg, bg, results)


EXPERIMENT_SETS = {'by_hansard': WordByHansard,
                   'by_month': WordByMonth,
                   'by_speaker': WordBySpeaker }


def main():
    args = docopt(__doc__)
    feature_name = args['<feature_name>']
    assert feature_name == 'words'
    assert args['<experimentset_name>'] in EXPERIMENT_SETS, '<experimentset_name> must be one of %s' % str(EXPERIMENT_SETS.keys())
    c = get_config()
    experiment_set = EXPERIMENT_SETS[args['<experimentset_name>']](feature_name=feature_name)

    print "Computing foreground group sums using %d cores..." % c.num_cores
    pool = Pool(c.num_cores, init_worker)
    fg_groups = experiment_set.list_foreground_groups()
    cache = {}
    try:
        for group_name, sum_vector in progress.bar(pool.imap_unordered(ComputeForegroundGroupSumCallable(experiment_set), fg_groups), label="Progress ", expected_size=len(fg_groups)):
            cache[group_name] = sum_vector
    except KeyboardInterrupt:
        print "Terminating pool.."
        pool.terminate()
        pool.join()

    print "Computing background sums..."
    bg_groups = experiment_set.list_background_groups()
    for g in bg_groups:
        sum_vector = experiment_set.compute_background_group_sum(g, cache)
        cache[g] = sum_vector

    print "Saving sums to ZODB..."
    zodb_root = open_zodb(read_only=False)
    if getattr(zodb_root, 'group_sums', None) is None:
        zodb_root.group_sums = BTrees.OOBTree.OOBTree()
        transaction.commit()
    if feature_name not in zodb_root.group_sums:
        zodb_root.group_sums[feature_name] = BTrees.OOBTree.OOBTree()
        transaction.commit()
    for k, v in cache.iteritems():
        zodb_root.group_sums[feature_name][k] = v
    transaction.commit()


    print "Creating output db tables..."
    create_db(c.resultsdb_url)
    session_out = open_db(c.resultsdb_url)

    print "Computing overrepresentation using %d cores..." % c.num_cores
    exps = experiment_set.list_experiments()
    cls = experiment_set.result_table_class()
    try:
        for fg, bg, results in progress.bar(pool.imap_unordered(ComputeOverrepresentedWordsCallable(experiment_set), exps), label="Progress ", expected_size=len(exps)):
            for w, odds, pval in results:
                c = cls(foreground_group_name=fg, background_group_name=bg, word=w, odds=odds, pval=pval)
                session_out.add(c)
    except KeyboardInterrupt:
        print "Terminating pool.."
        pool.terminate()
        pool.join()

    print "Committing..."
    session_out.commit()
    print "Done"
