# Presidential data

The scrapers are all located in `presidents/scraping/*.py` and rely on the `requests`, `BeautifulSoup4`, and `python-dateutil` libraries (among others). To install these libraries:

    pip install -r requirements.txt

See [Sources](docs/Sources.md) for documentation on where and how the data was collected.


# Presidential analysis

The substance of the analysis exists as IPython / Jupyter notebooks. See [`notebooks/`](notebooks/).

To setup [`spaCy` (1.9.0)](https://spacy.io/docs/):

    python -m spacy download en_core_web_md


## License

Copyright © 2017 Christopher Brown. [MIT Licensed](https://chbrown.github.io/licenses/MIT/#2017).
