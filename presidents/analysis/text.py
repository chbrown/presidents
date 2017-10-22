from __future__ import unicode_literals
import os
import operator
import itertools
import re
import string
from collections import Counter
import spacy
# relative imports
from .. import root
from ..readers import read_strings

# non-spaCy
# =========

stopwords_dirpath = os.path.join(root, 'stopwords')

stopwords = {
    'postgresql': set(read_strings(os.path.join(stopwords_dirpath, 'postgresql-english.txt'))),
    'nltk': set(read_strings(os.path.join(stopwords_dirpath, 'nltk-english.txt'))),
    'google_1t': set(read_strings(os.path.join(stopwords_dirpath, 'google-1t.txt'))),
    'datomic': set(read_strings(os.path.join(stopwords_dirpath, 'datomic.txt'))),
    'alphabet': set(string.ascii_lowercase),
    'contraction_suffixes': {'s', 'm', 're', 've', 'll', 'd', 't'},
    'contraction_prefixes': {'don', 'isn'},
}
_standard_stopwords_keys = ['google_1t', 'contraction_suffixes', 'contraction_prefixes']
standard_stopwords = {stopword for key in _standard_stopwords_keys for stopword in stopwords[key]}

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

# spaCy
# =====

nlp = spacy.en.English()
# add missing stop words (contractions whose lemmas are stopwords, mostly)
for word in ["'m", "'re", "'s", "ca", "n't", "'ill", "'ve", "'d"] + ['going', 'getting', 'got'] + ['-PRON-']:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True


def parse(document):
    '''
    Use the nlp object to parse the given document if it's a string or unicode,
    returning it unchanged if it's already a spacy.tokens.doc.Doc instance
    '''
    if isinstance(document, unicode):
        return nlp(document)
    elif isinstance(document, str):
        return nlp(document.decode())
    else:
        return document


def is_word(lexeme):
    '''
    Return true if the given spacy.lexeme.Lexeme (or vocabulary-indexed ID)
    is neither a stop word, nor punctuation, nor whitespace.
    '''
    if not isinstance(lexeme, spacy.lexeme.Lexeme):
        lexeme = nlp.vocab[lexeme]
    return not (lexeme.is_stop or lexeme.is_punct or lexeme.is_space)


def sentence_collocations(documents,
                          test_token=is_word,
                          map_token=lambda token: token.orth):
    '''
    documents: can be a list of strings or spacy.tokens.doc.Doc instances
    test_token: is a predicate that takes a Lexeme and returns True or False to
                determine whether to include it or not
    map_token: function that takes a Lexeme and returns a value to use for the
               values in the collocation pairs it returns

    return (token1, token2) pairs, duplicating each ordering, where each
    token value is whatever map_token returns; potentially an integer id
    resolvable in spaCy's Language vocab
    '''
    for document in documents:
        for sent in parse(document).sents:
            values = sorted(map_token(token) for token in sent if test_token(token))
            # to keep only one order, use itertools.combinations instead of permutations
            for value1, value2 in itertools.permutations(values, 2):
                if value1 != value2:
                    yield value1, value2


def sentence_collocation_counts(documents,
                                test_token=is_word,
                                map_token=lambda token: token.orth):
    '''
    return Counter (mapping) of ((value1, value2), count) pairs
    '''
    return Counter(sentence_collocations(documents, test_token, map_token))


def sentence_collocation_mapping(documents,
                                 test_token=is_word,
                                 map_token=lambda token: token.orth):
    '''
    iterates over pairs: value1 -> mapping of (value2 -> count)
    '''
    first = operator.itemgetter(0)
    second = operator.itemgetter(1)
    pairs = sentence_collocations(documents, test_token, map_token)
    for value1, pairs in itertools.groupby(sorted(pairs, key=first), first):
        yield value1, Counter(map(second, pairs))


def bootstrap_lexemes(lexemes, collocation_mapping, n):
    '''
    lexemes: integer ids
    collocation_mapping: dict/mapping of lexeme -> Counter(mapping of lexeme -> count)
    '''
    collocation_counters = (collocation_mapping.get(lexeme, Counter()) for lexeme in lexemes)
    for collocated_lexeme, _ in reduce(operator.add, collocation_counters).most_common(n):
        yield collocated_lexeme


def bootstrap_strings(strings, collocation_mapping, n,
                      map_token=lambda token: token.orth):
    '''
    tokens: list of strings to parse (usually, a list of a synset's tokens)
    collocation_mapping: dict/mapping of token -> Counter(mapping of token -> count)
    '''
    lexemes = {map_token(token) for token in parse(' '.join(strings))}
    for lexeme in lexemes:
        yield nlp.vocab[lexeme].orth_
    collocated_lexemes = set(bootstrap_lexemes(lexemes, collocation_mapping, n))
    for lexeme in collocated_lexemes - lexemes:
        yield nlp.vocab[lexeme].orth_
