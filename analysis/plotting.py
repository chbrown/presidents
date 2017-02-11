import numpy as np
import pandas as pd


_ordinal_mapping = {'First': '1st',
                    'Second': '2nd',
                    'Third': '3rd',
                    'Fourth': '4th'}
def iter_inaugural_titles(speeches):
    '''
    Prettify inaugural titles a little bit considering most presidents serve
    contiguous terms
    '''
    last_author = None
    for speech in speeches:
        author = speech.author
        title_ordinal = speech.title.split()[0]
        title = _ordinal_mapping[title_ordinal] if author == last_author else author
        yield '{}, {}'.format(title, speech.timestamp.year)
        last_author = author


def iter_comparisons(xs, cmp_func, label_func):
    # we prefer the nested for-loop because even itertools.permutations
    # excludes self-comparison
    labels = map(label_func, xs)
    for row, row_label in zip(xs, labels):
        for column, column_label in zip(xs, labels):
            yield row_label, column_label, cmp_func(row, column)


def create_pairwise_df(xs, cmp_func, label_func):
    '''
    xs: list of things to compare pairwise
    cmp_func: function from (x_i, x_j) to a numeric value
    label_func: function from (x_i) to a string label

    returns: square pd.DataFrame with len(xs) rows and columns
    '''
    df = pd.DataFrame.from_records(iter_comparisons(xs, cmp_func, label_func),
                                   columns=['row', 'column', 'value'])
    df_pivot = df.pivot(values='value', index='row', columns='column')
    # specify order of rows and columns
    labels = map(label_func, xs)
    return df_pivot[labels].reindex(labels)


def plot_pairwise_df(df, plt, cmap=None, gridcolor='lightgray', labelsize=8):
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
        # spine.set_edgecolor(gridcolor)
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
