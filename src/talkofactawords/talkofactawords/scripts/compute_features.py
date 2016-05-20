"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: compute_features script
The script reads english texts from a database (specified by <db_url> config parameter),
extracts features from texts (e.g. words or noun phrases) and stores computed results in a ZODB file.

Script runs in parallel using <num_cores> cores and stores the resulting database into
<zodb_dir> directory.

   Usage: compute_features [-h] <feature_name>

   where <feature_name> is either "words" or "noun_phrases" (or, more technically,
   a name of any callable defined in the talkofeuropewords.extract module).

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
import sys, signal
from multiprocessing import Pool
import transaction
import BTrees
from talkofactadb.model import Speech, open_db
import talkofactawords.extract
from talkofactadb.config import get_config
from talkofactawords.zodb import open_zodb
from docopt import docopt
from clint.textui import progress


def init_worker():
    # Ignore keyboard interrupts (will catch those in parent)
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class TaskRunner(object):
    def __init__(self, callable):
        self.callable = callable

    def __call__(self, speech):
        return (speech.id, self.callable(speech.speech))


def main():
    args = docopt(__doc__)
    extractor_name = args['<feature_name>']
    extractor = getattr(talkofactawords.extract, extractor_name, None)
    if extractor is None:
        print "Unknown extractor name"
        sys.exit(1)
    c = get_config()
    s = open_db()

    print "Preparing ZODB"
    zodb_root = open_zodb(read_only=False)
    if getattr(zodb_root, 'features', None) is None:
        zodb_root.features = BTrees.OOBTree.OOBTree()
        transaction.commit()
    if extractor_name not in zodb_root.features:
        zodb_root.features[extractor_name] = BTrees.OOBTree.OOBTree()
        transaction.commit()

    runner = TaskRunner(extractor)

    print "Querying database..."
    speeches = s.query(Speech).all()
    total_speeches = len(speeches)

    print "Computing using %d cores..." % c.num_cores
    pool = Pool(c.num_cores, init_worker)
    try:
        for i, (id, result) in enumerate(progress.bar(pool.imap_unordered(runner, speeches), label='Progress ', expected_size=total_speeches, every=100), 1):
            zodb_root.features[extractor_name][id] = result
            if i % 1000 == 0:
                transaction.commit()
        transaction.commit()
    except KeyboardInterrupt:
        print "Terminating pool.."
        pool.terminate()
        pool.join()

    print "Done"
