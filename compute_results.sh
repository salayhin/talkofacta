# Talk of ACTA analysis script
# The timings below correspond to num_cores = 20

# Create directories
mkdir -p data/zodb

export CONFIG=sample_config.py

# ---------- Convert CSV into DB ----------
# We use SQLite in our experiments
time bin/csv2db

# real    0m29.286s
# user    0m6.254s
# sys     0m0.852s

# ---------- Extract words from texts ----------
time bin/compute_features words

# real    4m3.213s
# user    7m34.046s
# sys     0m23.861s

# ---------- Compute set of common words to use in feature extraction ----------
time bin/collect_words

# real    1m11.987s
# user    0m55.790s
# sys     0m2.131s

# ---------- Extract country-specific words ----------
time bin/extract_significant_features words by_hansard

# real    4m43.433s
# user    45m27.883s
# sys     1m14.104s

# ---------- Extract month-specific words ----------
time bin/extract_significant_features words by_month

# real    1m21.643s
# user    5m57.680s
# sys     0m35.455s


# ---------- Extract year-specific words ----------
time bin/extract_significant_features words by_speaker

# real    12m36.825s
# user    128m29.229s
# sys     6m10.214s


# If you used default config (sample_config.py), at this point the results are
# all written out to the file <root_dir>/data/resultsdb.sqlite
# This file is used by the talkofeuropeweb visualization webapp (it is bundled with it).