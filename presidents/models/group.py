from dataclasses import dataclass
from typing import Callable, Iterable

import cytoolz as toolz

from presidents.util import slugify
from .speech import Speech


@dataclass(frozen=True)
class Group:
    name: str
    slug: str
    speeches: Iterable[Speech] = ()

    def __iter__(self):
        return iter(self.speeches)

    def __len__(self):
        return len(self.speeches)

    def __repr__(self):
        return f"<{type(self).__name__} {self.slug} {self.name!r} ({len(self)} speeches)>"

    @classmethod
    def from_predicates(
        cls,
        predicates: Iterable[Callable[[Speech], bool]],
        speeches: Iterable[Speech] = (),
        name: str = "Not Available",
        slug: str = None
    ):
        predicate = toolz.compose(all, toolz.juxt(predicates))
        return cls(name, slug or slugify(name), list(filter(predicate, speeches)))
