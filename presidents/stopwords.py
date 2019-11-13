from typing import Set

from presidents import DATA_DIR

contraction_suffixes = {"'s", "s",
                        "'m", "m",
                        "'re", "re",
                        "'ll", "ll",
                        "'ve", "ve",
                        "'d", "d",
                        "n't", "t"}
contraction_prefixes = {'ca', 'don', 'isn'}


def load_stopwords(name: str) -> Set[str]:
    """
    Currently available `name`s:
        datomic.txt
        google-1t.txt
        google-1t-10000.txt
        nltk-english.txt
        postgresql-english.txt
        spacy-english.txt
    """
    return set((DATA_DIR / "stopwords" / name).read_text().splitlines())


def load_standard_stopwords() -> Set[str]:
    return load_stopwords('google-1t.txt') | contraction_suffixes | contraction_prefixes
