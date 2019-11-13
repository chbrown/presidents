from dataclasses import dataclass
from typing import Container, Iterable, Iterator

import spacy.attrs

from .group import Group


@dataclass(frozen=True)
class Synset:
    name: str
    # `values` is presumably what spaCy would produce for `lower_`?
    # i.e., assert set(synset.values) == {token.lower_ for token in nlp(' '.join(synset.values))}
    values: Container[str]

    def __add__(self, other):
        cls = type(self)
        return cls(
            "+".join((self.name, other.name)),
            self.values + other.values,
        )


def synset_stats(
    group: Group,
    synset: Synset,
) -> Iterator[dict]:
    for speech in group.speeches:
        speech_counts = speech.count_words_by(spacy.attrs.LOWER)
        # number of synset matches in speech
        n_matches = sum(
            count
            for value, count in speech_counts.items()
            if value in synset.values
        )
        # total number of words in speech
        n_total = sum(speech_counts.values())
        yield {
            "group": group.name,
            "synset": synset.name,
            "n_matches": n_matches,
            "n_total": n_total,
            "proportion": n_matches / n_total,
        }


def all_synset_stats(
    groups: Iterable[Group],
    synsets: Iterable[Synset],
) -> Iterator[dict]:
    for group in groups:
        for synset in synsets:
            yield from synset_stats(group, synset)
