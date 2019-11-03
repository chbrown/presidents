import operator
import itertools
from functools import reduce
import re
from collections import Counter
import spacy

from . import logger
from .models import nlp, parse, is_word

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


def iter_substantive_words(tokens):
    '''
    Convert a sequence of tokens (can be strings or spaCy Token instances)
    into a (potentially shorter) sequence of lowercase strings.

    Discards tokens that are OOV, punctuation, whitespace, digits,
    or single letters (besides "a" and "I").
    '''
    for token in tokens:
        # convert to spaCy Lexeme if needed
        if not isinstance(token, (spacy.lexeme.Lexeme, spacy.tokens.Token)):
            token = nlp.vocab[token]
        # discard OOV, punctuation, spaces, and numbers
        if not (token.is_oov or token.is_punct or token.is_space or token.is_digit):
            text = token.text.lower()
            # discard single letters
            if len(text) > 1 or text in {'a', 'i'}:
                yield text


def token_counts(doc, attr_id=spacy.attrs.LOWER):
    '''
    Get a dict mapping tokens to counts for the given spaCy document, `doc`.

    By default the tokens are lowercased strings, but this can be customized
    by supplying a different `attr_id` value.
    '''
    return {nlp.vocab.strings[string_id]: count
            for string_id, count in doc.count_by(attr_id).items()
            if is_word(string_id)}


def token_freqs(doc, attr_id=spacy.attrs.LOWER):
    '''
    Like token_counts, but normalized so that all values sum to 1.
    '''
    doc_token_counts = token_counts(doc, attr_id)
    total = sum(doc_token_counts.values())
    return {token: count / total for token, count in doc_token_counts.items()}


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
    combined_counters = reduce(operator.add, collocation_counters)
    for collocated_lexeme, _ in combined_counters.most_common(n):
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


def context_spans(haystack_doc, needle_re, preceding_window, subsequent_window):
    '''
    Return tuples for each (potentially overlapping) match of needle_re within haystack_doc,
    of the form (preceding_span, match_span, subsequent_span), where each *_span is a spaCy Span instance.

    TODO: use doc.char_span(start, end, label=0, vector=None), introduced in spaCy v2.0.0a10
    See https://github.com/explosion/spaCy/issues/1264 and https://github.com/explosion/spaCy/issues/1050
    '''
    # haystack_idx_to_i maps each token's character index within the entire document to its index
    haystack_idx_to_i = {token.idx: token.i for token in haystack_doc}
    #logger.info('Finished mapping {} haystack token offsets to indices'.format(len(haystack_idx_to_i)))
    for match in needle_re.finditer(haystack_doc.text):
        # start, end = m.span()
        start = match.start()
        # not all matches will line up with a token
        if start in haystack_idx_to_i:
            token_i = haystack_idx_to_i[start]
            # calculate indices of windows; spaCy chokes on negative indices,
            # but indices greater than the largest are totally okay
            preceding_start = max(token_i - preceding_window, 0)
            # TODO: memoize this? most of the time group() will be the same, but
            # we need to check how long it is, in spaCy terms
            match_length = len(nlp(match.group(), tag=False, parse=False, entity=False))
            subsequent_start = token_i + match_length
            subsequent_end = subsequent_start + subsequent_window
            yield (haystack_doc[preceding_start:token_i],
                   haystack_doc[token_i:subsequent_start],
                   haystack_doc[subsequent_start:subsequent_end])
        else:
            logger.debug('Failed to find token at idx=%d', start)


def context_tokens(haystack_doc, needle_re, preceding_window, subsequent_window):
    '''
    Iterate over all the Tokens in all the pre/post context Spans
    of all the matches of needle_re within haystack_doc.
    '''
    for pre_span, _, post_span in context_spans(haystack_doc, needle_re, preceding_window, subsequent_window):
        for span in [pre_span, post_span]:
            for token in span:
                yield token
