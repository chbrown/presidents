from __future__ import division, unicode_literals
import os
import re
import string
from collections import Counter
import spacy
# relative imports
from . import root
from .readers import read_strings

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

# spaCy
# =====

nlp = spacy.load('en_core_web_md')
# add missing stop words (contractions whose lemmas are stopwords, mostly)
for word in ["'m", "'re", "'s", "ca", "n't", "'ill", "'ve", "'d"] + ['going', 'getting', 'got'] + ['-PRON-']:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True


def is_word(lexeme):
    '''
    Return true if the given spacy.lexeme.Lexeme (or vocabulary-indexed ID)
    is neither a stop word, nor punctuation, nor whitespace.
    '''
    if not isinstance(lexeme, (spacy.lexeme.Lexeme, spacy.tokens.Token)):
        lexeme = nlp.vocab[lexeme]
    return not (lexeme.is_stop or lexeme.is_punct or lexeme.is_space)


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
