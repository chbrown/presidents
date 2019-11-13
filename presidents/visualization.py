from pathlib import Path
from typing import Iterable, Iterator
import logging
import subprocess

import altair as alt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def export_altair_chart(chart: alt.Chart, basename: str, dirpath: Path):
    '''
    Render the given chart to a PDF at {dirpath}/{basename}.pdf
    Write the raw Vega-Lite JSON to {dirpath}/{basename}.vl.json

    May need to install dependencies:
        brew install svg2pdf
        npm config set python python2.7
        npm install -g vega@2.6.5 vega-lite@1.3.1
    '''
    if not isinstance(chart, alt.Chart):
        raise RuntimeError('chart must be an altair.Chart instance')
    if basename.endswith('.pdf'):
        raise RuntimeError('basename should not end in .pdf')

    vl_json_filepath = dirpath / f'{basename}.vl.json'
    pdf_filepath = dirpath / f'{basename}.pdf'

    vl_json_string = chart.to_json()
    try:
        with open(vl_json_filepath, 'x') as vl_json_file:
            vl_json_file.write(vl_json_string)
        logger.info('Wrote Vega-Lite to %s', vl_json_filepath)
    except FileExistsError as exc:
        logger.warning('Not writing Vega-Lite: %s', exc)

    try:
        vl2svg_proc = subprocess.run(['vl2svg'], stdout=subprocess.PIPE, input=vl_json_string,
                                     universal_newlines=True, check=True)
        svg_string = vl2svg_proc.stdout
        with open(pdf_filepath, 'xb') as pdf_file:
            svg2pdf_proc = subprocess.run(['svg2pdf'], stdout=pdf_file, input=svg_string,
                                          encoding='utf-8', check=True)
        logger.info('Wrote PDF to "%s"', pdf_filepath)
    except FileExistsError as exc:
        logger.warning('Not writing PDF: %s', exc)


_ordinal_mapping = {'First': '1st',
                    'Second': '2nd',
                    'Third': '3rd',
                    'Fourth': '4th'}


def iter_inaugural_titles(speeches: Iterable) -> Iterator[str]:
    '''
    Prettify inaugural titles a little bit considering most presidents serve
    contiguous terms
    '''
    last_author = None
    for speech in speeches:
        author = speech.author
        title_ordinal = speech.title.split()[0]
        title = _ordinal_mapping[title_ordinal] if author == last_author else author
        yield f'{title}, {speech.timestamp.year}'
        last_author = author


def create_pairwise_df(xs, cmp_func, label_func):
    '''
    xs: list of things to compare pairwise
    cmp_func: function from (x_i, x_j) to a numeric value
    label_func: function from (x_i) to a string label

    returns: square pd.DataFrame with len(xs) rows and columns
    '''
    df = pd.DataFrame(
        {
            'row': label_func(row),
            'column': label_func(column),
            'value': cmp_func(row, column),
        }
        for row in xs
        for column in xs
    )
    df_pivot = df.pivot(index='row', columns='column', values='value')
    # specify order of rows and columns
    labels = list(map(label_func, xs))
    return df_pivot[labels].reindex(labels)


def plot_pairwise_df(df: pd.DataFrame, plt, cmap=None, labelsize: int = 8):
    if cmap is None:
        cmap = plt.cm.hot_r
    # display NaN values as white (though apparently this is the default for hot_r)
    cmap.set_bad(color='w')
    # pcolor{,mesh} isn't very smart about NaNs when normalizing so we set v{min,max} manually
    vmin = df.min().min()
    vmax = df.max().max()
    plt.pcolormesh(df, cmap=cmap, vmin=vmin, vmax=vmax, edgecolors=None)
    ax = plt.axes()
    # set outer borders to same color as internal grid
    for spine in ax.spines.values():
        # spine.set_edgecolor('lightgray')
        spine.set_visible(False)
    # set up x-axis
    ax.set_yticks(np.arange(df.shape[0]) + 0.5, minor=False)
    ax.set_yticklabels(df.index, minor=False, size=labelsize)
    ax.set_ylabel(df.index.name.title())
    # set up y-axis
    ax.set_xticks(np.arange(df.shape[1]) + 0.5, minor=False)
    ax.set_xticklabels(df.columns, minor=False, size=labelsize, rotation=90)
    ax.set_xlabel(df.columns.name.title())
    return ax
