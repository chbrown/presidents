from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Dict, Mapping

import spacy
from spacy.tokens import Doc

from presidents.text import load_nlp, count_words_by
from presidents.util import parse_date, tzinfos, elide, hashabledict


@dataclass(frozen=True)
class Speech:
    title: str
    author: str
    text: str
    source: str
    timestamp: datetime
    metadata: Mapping

    def __repr__(self):
        contents = [
            f"title={self.title!r}",
            f"author={self.author!r}",
            f"text={elide(self.text)!r}",
            f"source={self.source!r}",
            f"timestamp={self.timestamp!r}",
            self.metadata and f"metadata={self.metadata!r}",
        ]
        return f"{type(self).__name__}({', '.join(filter(None, contents))})"

    @classmethod
    def from_json(cls, title: str, author: str, text: str, source: str, timestamp: str, **metadata):
        timestamp = parse_date(timestamp, tzinfos['EST'])
        metadata = hashabledict(metadata)
        return cls(title, author, text, source, timestamp, metadata)

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "text": self.text,
            "source": self.source,
            "timestamp": self.timestamp,  # maybe convert to str?
            **self.metadata,
        }

    @property
    @lru_cache()
    def doc(self) -> Doc:
        nlp = load_nlp()
        return nlp(self.text)

    @lru_cache()
    def count_words_by(self, attr_id: int = spacy.attrs.ORTH) -> Dict[str, int]:
        return count_words_by(self.doc, attr_id)
