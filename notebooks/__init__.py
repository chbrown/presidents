import re
import json
import string
from collections import Counter

def select(d, whitelist):
    '''
    Construct a dict from a subset of `d`, limited to keys that are in `whitelist`
    '''
    return {k: v for k, v in d.items() if k in whitelist}

def read_lines(filepaths):
    '''
    Iterate over all lines in all files listed by `filepaths`
    '''
    for filepath in filepaths:
        with open(filepath) as fp:
            for line in fp:
                yield line

def read_strings(filepath):
    '''
    Read each line from `filepath` as a string without line separators
    '''
    with open(filepath) as fp:
        for line in fp:
            yield line.rstrip()

def read_ldjson(filepath):
    '''
    Read each line from `filepath` as a JSON object
    '''
    with open(filepath) as fp:
        for line in fp:
            yield json.loads(line)

stopwords = {
    'postgresql': set(read_strings('stopwords/postgresql-english.txt')),
    'nltk': set(read_strings('stopwords/nltk-english.txt')),
    'google_1t': set(read_strings('stopwords/google-1t.txt')),
    'datomic': set(read_strings('stopwords/datomic.txt')),
    'alphabet': set(string.ascii_lowercase),
    'contraction_suffixes': {'s', 'm', 're', 've', 'll', 'd', 't'},
    'contraction_prefixes': {'don', 'isn'},
}
standard_stopwords = {stopword
    for key in ['google_1t', 'contraction_suffixes', 'contraction_prefixes']
        for stopword in stopwords[key]}

_non_linguistic = [
    'applause', 'cheers and applause', 'laughter',
    'booing', 'boos', 'crosstalk', 'inaudible', 'silence']
_non_linguistic_pattern = r'\[(' + '|'.join(_non_linguistic) + r')\]'

def tokenize(s, stopwords=None):
    # normalize abbreviations to avoid stranded initials
    s = re.sub(r'(?:[A-Z]\.)+', lambda m: m.group(0).replace('.', ''), s)
    # normalize numbers to avoid 000 turning up as a significant token
    s = re.sub(r',(\d{3})\b', r'\1', s)
    # leave out non-linguistic content
    s = re.sub(_non_linguistic_pattern, ' ', s, flags=re.I)
    # "justice" gets special treatment
    s = re.sub(r'Chief Justice', ' ', s)
    # replace all non-alphanumerics with spaces
    s = re.sub(r'[^\w]', ' ', s)
    for token in s.lower().strip().split():
        if stopwords is None or token not in stopwords:
            yield token

def iter_speech_counts(speech, synsets, stopwords=None):
    speech_without_text = {k: v for k, v in speech.items() if k != 'text'}
    counts = Counter(tokenize(speech['text'], stopwords))
    total_count = sum(counts.values())
    for synset_name, synset_tokens in synsets:
        synset_count = sum(counts.get(synset_token, 0) for synset_token in synset_tokens)
        yield dict(synset=synset_name,
                   synset_count=synset_count,
                   synset_proportion=float(synset_count) / float(total_count),
                   total_count=total_count,
                   **speech_without_text)

def iter_speeches_counts(speeches, synsets, stopwords=None):
    for i, speech in enumerate(speeches):
        for speech_count in iter_speech_counts(speech, synsets, stopwords):
            yield dict(id=i, **speech_count)

def iter_groups_speeches_count(groups, synsets, stopwords=None):
    '''
    groups: a list of (group_name, group_speeches) pairs
    synsets: a list of (synset_name, synset_matches) pairs

    Iterates over dicts built from the items in group_speeches, but without the
    'text' field, and with the following additional fields:
    * synset: string
    * synset_count: int
    * synset_proportion: float
    * total_count: int
    * id: int - enumerated identifier that is only unique _within each group_
    * group: string - the group_name that is paired with the speech
    '''
    for group_name, group_speeches in groups:
        for speech_count in iter_speeches_counts(group_speeches, synsets, stopwords):
            yield dict(group=group_name, **speech_count)
