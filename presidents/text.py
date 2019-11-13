from collections import Counter
from functools import lru_cache, reduce
from typing import Callable, Dict, Iterable, Iterator, List, Tuple, TypeVar
import itertools
import logging
import operator

from spacy.tokens import Doc, Token
from spacy.lexeme import Lexeme
import cytoolz as toolz
import spacy

from presidents.stopwords import contraction_suffixes

logger = logging.getLogger(__name__)


@lru_cache()
def load_nlp():
    nlp = spacy.load('en_core_web_md', disable=['parser', 'ner'])
    nlp.max_length = 10_000_000
    # add missing stop words (contractions whose lemmas are stopwords, mostly)
    for stopword_string in contraction_suffixes | {'going', 'getting', 'got'} | {'-PRON-'}:
        nlp.vocab[stopword_string].is_stop = True
    logger.info("Loaded %(lang)s-%(name)s with pipeline=%(pipeline)s (v%(version)s)", nlp.meta)
    return nlp


def _is_substantive(lexeme: Lexeme) -> bool:
    return all((
        not lexeme.is_oov,
        not lexeme.is_punct,
        not lexeme.is_space,
        not lexeme.is_digit,
        len(lexeme.text) > 1 or lexeme.text in {'A', "I", 'a', 'i'},
    ))


def iter_substantive_words(tokens: Iterable[Token]) -> List[str]:
    """
    Convert a sequence of tokens into a (potentially shorter) sequence of lowercase strings.

    Discards tokens that are OOV, punctuation, whitespace, digits, or single letters (besides "a" and "I").
    """
    return [token.text.lower() for token in tokens if _is_substantive(token)]


def _is_word(lexeme: Lexeme) -> bool:
    """
    Return true if the `lexeme` is neither a stop word, nor punctuation, nor whitespace.
    """
    return not (lexeme.is_stop or lexeme.is_punct or lexeme.is_space)


def count_words_by(doc: Doc, attr_id: int = spacy.attrs.ORTH) -> Dict[str, int]:
    """
    Get a dict mapping tokens to counts for the given spaCy document, `doc`.
    By default the tokens are the observed strings, but this can be customized
    by supplying a different `attr_id` value, like LOWER, for lowercased tokens.
    """
    # other popular attr_id values: spacy.attrs.LEMMA, spacy.attrs.LOWER
    vocab = doc.vocab
    counts = doc.count_by(attr_id)
    return {
        vocab.strings[attribute]: count
        for attribute, count in counts.items()
        if _is_word(vocab[attribute])
    }


def freq_words_by(doc: Doc, attr_id: int = spacy.attrs.ORTH) -> Dict[str, float]:
    """
    Like `count_words_by`, but normalized so that all values sum to 1.
    """
    counts = count_words_by(doc, attr_id)
    total = sum(counts.values())
    return {token: count / total for token, count in counts.items()}


X = TypeVar("X")
Y = TypeVar("Y")


def collocations(
    xs: Iterable[X],
    test: Callable[[X], bool] = lambda _: True,
    f: Callable[[X], Y] = toolz.identity,
) -> Iterator[Tuple[Y, Y]]:
    """
    Return tuples for every pair of ys, where y = f(x) and x is discarded if ¬test(x)
    """
    # to keep only one order, use `combinations` instead of `permutations`
    return itertools.permutations(sorted(f(x) for x in xs if test(x)), r=2)


def sentence_collocations(docs: Iterable[Doc],
                          test_token=_is_word,
                          map_token=lambda token: token.orth):
    '''
    test_token: predicate that takes a Lexeme and returns True or False to
                determine whether to include it or not
    map_token: function that takes a Lexeme and returns a value to use for the
               values in the collocation pairs it returns

    return (token1, token2) pairs, duplicating each ordering, where each
    token value is whatever map_token returns; potentially an integer id
    resolvable in spaCy's Language vocab
    '''
    for doc in docs:
        for sent in doc.sents:
            for value1, value2 in collocations(sent, test_token, map_token):
                if value1 != value2:
                    yield value1, value2


# return Counter like {(value1, value2): count}
sentence_collocation_counts = toolz.compose(Counter, sentence_collocations)


def sentence_collocation_mapping(docs: Iterable[Doc],
                                 test_token=_is_word,
                                 map_token=lambda token: token.orth):
    '''
    iterates over pairs: value1 -> mapping of (value2 -> count)
    '''
    first = operator.itemgetter(0)
    second = operator.itemgetter(1)
    pairs = sentence_collocations(docs, test_token, map_token)
    for value1, pairs in itertools.groupby(sorted(pairs, key=first), first):
        yield value1, Counter(map(second, pairs))


def bootstrap_lexemes(lexemes: Iterable[int], collocation_mapping: Dict[int, Counter], n: int) -> int:
    '''
    lexemes: integer ids
    collocation_mapping: dict/mapping of lexeme -> Counter(mapping of lexeme -> count)
    '''
    counters = [collocation_mapping.get(lexeme, Counter()) for lexeme in lexemes]
    total_counter = reduce(operator.add, counters)
    for lexeme, _ in total_counter.most_common(n):
        yield lexeme


def bootstrap_strings(strings: List[str], collocation_mapping: Dict[int, Counter], n: int,
                      map_token=lambda token: token.orth):
    '''
    tokens: list of strings to parse (usually, a list of a synset's tokens)
    collocation_mapping: dict/mapping of token -> Counter(mapping of token -> count)
    '''
    nlp = load_nlp()
    lexemes = {map_token(token) for token in nlp(' '.join(strings))}
    for lexeme in lexemes:
        yield nlp.vocab[lexeme].orth_
    collocated_lexemes = set(bootstrap_lexemes(lexemes, collocation_mapping, n))
    for lexeme in collocated_lexemes - lexemes:
        yield nlp.vocab[lexeme].orth_


def context_spans(haystack_doc: Doc, needle_re, preceding_window: int, subsequent_window: int):
    '''
    Return tuples for each (potentially overlapping) match of needle_re within haystack_doc,
    of the form (preceding_span, match_span, subsequent_span), where each *_span is a spaCy Span instance.

    TODO: use doc.char_span(start, end, label=0, vector=None), introduced in spaCy v2.0.0a10
    See https://github.com/explosion/spaCy/issues/1264 and https://github.com/explosion/spaCy/issues/1050
    '''
    nlp = load_nlp()
    # haystack_idx_to_i maps each token's character index within the entire document to its index
    haystack_idx_to_i = {token.idx: token.i for token in haystack_doc}
    # logger.info('Finished mapping {} haystack token offsets to indices'.format(len(haystack_idx_to_i)))
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
            match_length = len(nlp(match.group(), disable=["tagger", "parser", "ner"]))
            subsequent_start = token_i + match_length
            subsequent_end = subsequent_start + subsequent_window
            yield (haystack_doc[preceding_start:token_i],
                   haystack_doc[token_i:subsequent_start],
                   haystack_doc[subsequent_start:subsequent_end])
        else:
            logger.debug('Failed to find token at idx=%d', start)


def context_tokens(haystack_doc: Doc, needle_re, preceding_window, subsequent_window: int):
    '''
    Iterate over all the Tokens in all the pre/post context Spans
    of all the matches of needle_re within haystack_doc.
    '''
    for pre_span, _, post_span in context_spans(haystack_doc, needle_re, preceding_window, subsequent_window):
        for span in [pre_span, post_span]:
            for token in span:
                yield token
