import os
from pathlib import Path

import spacy

from . import root

# non-spaCy
# =========

contraction_suffixes = {"'s", "s",
                        "'m", "m",
                        "'re", "re",
                        "'ll", "ll",
                        "'ve", "ve",
                        "'d", "d",
                        "n't", "t"}
contraction_prefixes = {'ca', 'don', 'isn'}

_stopwords_dir = Path(root) / 'stopwords'
# postgresql_stopwords = set((_stopwords_dir / 'postgresql-english.txt').read_text().splitlines())
# nltk_stopwords = set((_stopwords_dir / 'nltk-english.txt').read_text().splitlines())
# datomic_stopwords = set((_stopwords_dir / 'datomic.txt').read_text().splitlines())
google_1t_stopwords = set((_stopwords_dir / 'google-1t.txt').read_text().splitlines())

standard_stopwords = google_1t_stopwords | contraction_suffixes | contraction_prefixes

# spaCy
# =====

nlp = spacy.load('en_core_web_md')
# add missing stop words (contractions whose lemmas are stopwords, mostly)
for stopword_string in contraction_suffixes | {'going', 'getting', 'got'} | {'-PRON-'}:
    stopword_lexeme = nlp.vocab[stopword_string]
    stopword_lexeme.is_stop = True


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
