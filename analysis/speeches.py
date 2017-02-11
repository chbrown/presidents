from collections import Counter
from spacy import attrs
import dateutil.parser

from readers import read_ldjson
import text


def iter_speech_counts(speech, synsets, stopwords=None):
    speech_without_text = {k: v for k, v in speech.items() if k != 'text'}
    counts = Counter(text.tokenize(speech['text'], stopwords))
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
    return {k: v for k, v in document.count_by(attr).iteritems() if text.is_word(v)}


class Speech(object):
    '''
    spaCy-oriented document container; lazy, memoized
    '''
    def __init__(self, text, **kwargs):
        self.text = text
        self.metadata = kwargs

    @property
    def author(self):
        return self.metadata['author']

    @property
    def title(self):
        return self.metadata['title']

    @property
    def timestamp(self):
        timestamp_str = self.metadata['timestamp']
        return dateutil.parser.parse(timestamp_str)

    @property
    def source(self):
        return self.metadata['source']

    @property
    def document(self):
        if not hasattr(self, '_document'):
            # doc = nlp(text)
            # is equivalent to:
            # doc = nlp.tokenizer(text); nlp.tagger(doc); nlp.parser(doc); nlp.entity(doc)
            # but for our purposes (so far), mostly what we need is the tokenization
            # and the embedding, which we get with just the tokenizer call
            self._document = text.nlp.tokenizer(self.text)
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
    def __init__(self, filepaths, predicate = lambda speech: True):
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
