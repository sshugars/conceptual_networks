import os
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

inpath = '../data/MTurk/'
outpath = '../../figs/'
os.chdir(inpath)


# for consistency across visualizations,
# sorted by eigenvectors of full data
personality = [
    'Purity (MF)',
    'Authority (MF)',
    'Ideology',
    'Neuroticism (Big 5)',
    'Ingroup (MF)',
    'Extroversion (Big 5)',
    'Agreeableness (Big 5)',
    'Harm (MF)',
    'Conscientiousness (Big 5)',
    'Fairness (MF)',
    'Knowledge',
    'Openness (Big 5)',
    'Deliberation',
    'Progressivism (MF)'
]

demographics = [
    'gender (M)',
    'Race (white NH)',
    'religiosity',
    'age',
    'partyid (R)',
    'income',
    'education'
]

stats = [
         'k avg',
         'k std',
         'entropy',
         'clustering',
         'giant component',
         'disssortativity', 
         'density'
]


def get_sorted_corr(corr, col_order = list(), row_order = list()):

    # column order
    if not col_order:
        sq = corr.T.dot(corr)
        val, vec = np.linalg.eig(sq)

        # find largest eigenvalue
        index = np.where(val == max(val))[0][0]

        # return largest eigenvector as strength
        vector = vec.T[index]

        order_dict = dict((j,i) for i, j in enumerate(vector))
        newcols = [i for j, i in sorted(order_dict.items())]

        cols = corr.columns.tolist()
        col_order = [cols[i] for i in newcols]

    # row order
    if not row_order:
        sq = corr.dot(corr.T)
        val, vec = np.linalg.eig(sq)

        # find largest eigenvalue
        index = np.where(val == max(val))[0][0]

        # return largest eigenvector as strength
        vector = vec.T[index]

        order_dict = dict((j,i) for i, j in enumerate(vector))
        newrows = [i for j, i in sorted(order_dict.items())]

        rows = corr.index.tolist()
        row_order = [rows[i] for i in newrows][::-1]

    sorted_corr = corr[col_order].reindex(row_order)

    return sorted_corr


def single_plot(corr, outfile):
    plt.rcParams.update({'font.size': 14})
    f, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(corr,
                vmin=-4, vmax=4,
                cmap=sns.diverging_palette(h_neg=10, h_pos=240, n=5, as_cmap=False, center='light'),
                ax=ax1, linewidths=.01, cbar=False)

    for tick in ax.get_yticklabels():
        tick.set_rotation(0)

    plt.savefig(outfile, format='pdf', bbox_inches='tight')
    plt.close()
    print('Figure saved to file %s.' % outfile)


def double_plot(pers_corr, dem_corr, outfile):
    plt.rcParams.update({'font.size': 14})

    f, (ax1, ax2, axcb) = plt.subplots(1, 3,
                gridspec_kw={'width_ratios':[1,.5,0.06]},
                                   figsize=(14, 7))

    ax1.get_shared_y_axes().join(ax2)


    g1 = sns.heatmap(pers_corr,
                vmin=-4, vmax=4,
                cmap=sns.diverging_palette(h_neg=10, h_pos=240, n=5, as_cmap=False, center='light'),
                ax=ax1, linewidths=.01, cbar=False)

    g1.set_ylabel('')
    g1.set_xlabel('')

    g2 = sns.heatmap(dem_corr,
                vmin=-4, vmax=4,
                cmap=sns.diverging_palette(h_neg=10, h_pos=240, n=5, as_cmap=False, center='light'),
                ax=ax2, linewidths=.25, cbar_ax=axcb)

    g2.set_ylabel('')
    g2.set_xlabel('')
    g2.set_yticks([])

    # may be needed to rotate the ticklabels correctly:
    for ax in [g1, g2]:
        tl = ax.get_xticklabels()
        ax.set_xticklabels(tl, rotation=90)
        tly = ax.get_yticklabels()
        ax.set_yticklabels(tly, rotation=0)

    plt.savefig(outfile, format='pdf', bbox_inches='tight')
    plt.close()
    print('Figure saved to file %s.' % outfile)


def main():
    filename = input('Enter correlation file to visualize.\n')

    while not os.path.exists(filename):
        print('No file with name %s found.' %filename)
        filename = input('Enter correlation file to visualize.\n')

    try:
        corr = pd.read_csv(filename, index_col=0)
        pers_corr = get_sorted_corr(corr[personality], col_order=personality, row_order=stats)
        dem_corr = get_sorted_corr(corr[demographics], col_order=demographics, row_order=stats)

        if filename == 'estimated_corr.txt':
            outfile = outpath + 'personality_corr.pdf'
        else:
            file_suffix = '_'.join(filename.split('.')[0].split('_')[2:])
            outfile = outpath + 'personality_corr_%s.pdf' % file_suffix

        double_plot(pers_corr, dem_corr, outfile)

    except userException:
        print('Unable to process file.')

main()