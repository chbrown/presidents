from __future__ import division, unicode_literals
import os
import string
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

# spaCy
# =====

nlp = spacy.load('en_core_web_md')
# add missing stop words (contractions whose lemmas are stopwords, mostly)
for stop_string in ["'m", "'re", "'s", "ca", "n't", "'ill", "'ve", "'d"] + ['going', 'getting', 'got'] + ['-PRON-']:
    stop_lexeme = nlp.vocab[stop_string]
    stop_lexeme.is_stop = True


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
    if isinstance(document, spacy.tokens.doc.Doc):
        return document
    return nlp(document)
