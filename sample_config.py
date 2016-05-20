# Sample configuration file
# Specifies parameters used by scripts in talkofeuropedb & talkofactawords packages.
import os

root_dir = os.path.abspath(os.path.dirname(os.getenv('CONFIG')))

# Directory for storing CSV & SQLITE files with text data
textdb_dir = root_dir + '/data/textdb'

# Directory for keeping the zodb.fs file with precomputed feature vectors
zodb_dir = root_dir + '/data/zodb'

# Database URL for importing Speech data
db_url = "sqlite:///%s/acta.sqlite" % textdb_dir

# Database URL for storing overrepresentation analysis results (extract_significant_features script)
resultsdb_url = "sqlite:///%s/data/resultsdb.sqlite" % root_dir

# Number of cores to use for parallel tasks
num_cores = 20


# Config parameters used in Flask config
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(root_dir, 'src/talkofactaweb/data/resultsdb.sqlite')
DEBUG = False
SQLALCHEMY_ECHO = False
