from __future__ import unicode_literals, print_function
import itertools
from collections import Counter
from spacy.en import English

nlp = English()
# add missing stop words (contractions whose lemmas are stopwords, mostly)
for word in ["'m", "'re", "'s", "ca", "n't", "'ill", "'ve", "'d"] + ['going', 'getting', 'got']:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

def parse(document):
    if isinstance(document, unicode):
        return nlp(document)
    elif isinstance(document, str):
        return nlp(document.decode())
    else:
        return document

def _is_word(token):
    return not (token.is_stop or token.is_punct or token.is_space)

def sentence_collocations(documents):
    for document in documents:
        for sent in nlp(document).sents:
            # token.lemma is an int
            lemmas = sorted(token.lemma for token in sent if _is_word(token))
            for lemma1, lemma2 in itertools.combinations(lemmas, 2):
                yield lemma1, lemma2

def sentence_collocation_counts(documents):
    return Counter(sentence_collocations(documents))
