# Presidential data & analysis

* The scrapers are all located in [`presidents/scrapers/*.py`](presidents/scrapers/).

  See [Sources](docs/Sources.md) for documentation on where and how the data was collected.

* The substance of the analysis exists as Jupyter notebooks in [`notebooks/`](notebooks/).


## Installation

These instructions assume you already have Python 3 installed.

In addition to the Python packages installed in the next section,
you'll need to install a few non-Python dependencies on your system:

* On macOS with [Homebrew](https://brew.sh/):

      brew install cairo py3cairo jpeg jpeg-turbo node

* On CentOS 7:

      yum -y groupinstall development
      yum -y install cairo-devel cairo-tools
      yum -y install libjpeg-turbo libjpeg-turbo-devel
      yum -y install nodejs nodejs-devel
      yum -y install https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm
      fc-cache /usr/share/fonts/msttcore

Once you have Node.js & `npm` installed:

    npm install -g vega vega-lite

Get the LIWC 2007 dictionary (see [`liwc-python`](https://github.com/chbrown/liwc-python) for details) and move it to:

    /usr/local/data/liwc_2007.dic

### Python dependencies and environment

It's recommended to sandbox everything into a [virtualenv](https://virtualenv.pypa.io/en/stable/),
which makes installation more predictable / reliable:

    pip install -U virtualenv
    virtualenv ~/presidents-venv
    source ~/presidents-venv/bin/activate

Now that you've activated the virtualenv, get the code:

    git clone https://github.com/chbrown/presidents ~/presidents
    cd ~/presidents

The scrapers rely on the `requests`, `BeautifulSoup4`, and `python-dateutil` libraries (among others),
with the Jupyter notebooks requiring many more. To install these:

    pip install -r requirements.txt

Then, install `presidents` as a package so that Jupyter Lab can import and use its modules:

    pip install -e .

Start the Jupyter Lab server:

    jupyter lab notebooks


## License

Copyright © 2017–2019 Christopher Brown.
[MIT Licensed](https://chbrown.github.io/licenses/MIT/#2017-2019).
