import sys
from collections import Counter, Mapping
from spacy import attrs
# relative imports
from .text import tokenize, is_word, nlp, parse
from ..readers import read_ldjson
from .. import parse_date, tzinfos, logger


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


def _count_words(document, attr):
    return {k: v for k, v in document.count_by(attr).items() if is_word(k)}


class TitledDocument(Mapping):
    attrs = ('title', 'text')

    def __init__(self, title, text, **kwargs):
        self.title = title
        self.text = text
        self.metadata = kwargs

    # collections.Mapping ABC implementation
    def __len__(self):
        return len(self.attrs) + len(self.metadata)

    def __iter__(self):
        for attr in self.attrs:
            yield attr
        for key in self.metadata:
            yield key

    def __getitem__(self, key):
        if key in self.attrs:
            return getattr(self, key)
        return self.metadata[key]

    @property
    def document(self):
        if not hasattr(self, '_document'):
            self._document = parse(self.text)
        return self._document


class Speech(Mapping):
    attrs = {'title', 'author', 'text', 'source', 'timestamp'}

    '''
    spaCy-oriented document container; lazy, memoized
    '''
    def __init__(self, title, author, text, source, timestamp, **kwargs):
        self.title = title
        self.author = author
        self.text = text
        self.source = source
        self.timestamp = parse_date(timestamp, tzinfos['EST'])
        # logger.error("Could not parse timestamp '{}' in metadata: {}".format(timestamp_str, self.metadata))
        self.metadata = kwargs

    @property
    def date(self):
        return self.timestamp.date()

    # collections.Mapping ABC implementation
    def __len__(self):
        return len(self.attrs) + len(self.metadata)

    def __iter__(self):
        for attr in self.attrs:
            yield attr
        for key in self.metadata:
            yield key

    def __getitem__(self, key):
        if key in self.attrs:
            return getattr(self, key)
        return self.metadata[key]

    # (memoized) spaCy interface
    @property
    def document(self):
        if not hasattr(self, '_document'):
            self._document = parse(self.text)
        return self._document

    @property
    def lemma_counts(self):
        if not hasattr(self, '_lemma_counts'):
            self._lemma_counts = _count_words(self.document, attrs.LEMMA)
        return self._lemma_counts

    @property
    def orth_counts(self):
        if not hasattr(self, '_orth_counts'):
            self._orth_counts = _count_words(self.document, attrs.ORTH)
        return self._orth_counts

    @property
    def lower_counts(self):
        if not hasattr(self, '_lower_counts'):
            self._lower_counts = _count_words(self.document, attrs.LOWER)
        return self._lower_counts


# The Speech class API should be mostly stable, but the SpeechCollection feels
# too thin to merit its own class, so it may change / get simplified in the future.

class SpeechCollection(object):
    def __init__(self, filepaths, predicate=lambda speech: True):
        self.filepaths = filepaths
        self.predicate = predicate

    def __iter__(self):
        for speech_dict in read_ldjson(*self.filepaths):
            speech = Speech(**speech_dict)
            if self.predicate(speech):
                yield speech

    def __len__(self):
        return len(self.speeches)

    @property
    def speeches(self):
        if not hasattr(self, '_speeches'):
            self._speeches = list(iter(self))
        return self._speeches
