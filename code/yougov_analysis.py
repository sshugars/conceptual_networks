import os
import json
import pandas as pd
import numpy as np
import scipy.stats as sp
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler
import random
import matplotlib.pyplot as plt
import matplotlib

# ------------- data paths -------------- #
path = '../data/YouGov/'
plot_path = '../../figs/'
os.chdir(path)

# ----------plot settings -------------- #
matplotlib.rc('xtick', labelsize=13) 
matplotlib.rc('ytick', labelsize=13) 
matplotlib.rc('xtick.major', size=4, width=1)
matplotlib.rc('xtick.minor', size=1, width=1)
matplotlib.rc('ytick.major', size=4, width=1)
matplotlib.rc('ytick.minor', size=1, width=1)
matplotlib.rc('axes', edgecolor='504A4B')  # axes edge color
matplotlib.rc('axes', grid=False)  # display grid or not
matplotlib.rc('axes', titlesize=20)   # fontsize of the axes title
matplotlib.rc('axes', labelsize=15)  # fontsize of the x and y labels

matplotlib.rc('lines', linewidth=2.0)     # line width in points

matplotlib.rc('legend', fontsize=16)

matplotlib.rc('figure', figsize=(10, 6))    # figure size in inches
matplotlib.rc('figure', facecolor='ffffff')    # figure facecolor


# ----------regression models -------------- #
scaler = MinMaxScaler()
random.seed(7684)

model1 = ['word_count',
          'FK']

model2 = ['clustering',
           'giant_component', 
           'disssortativity', 
           'k_avg', 
           'k_std', 
           'entropy',
           'density']

model3 = model1 + model2

formulas = dict((i + 1, 'y ~ ' + ' + '.join(model)) for i, model in enumerate([model1, model2, model3]))


# ----------Helper functions -------------- #
def get_cumulative(data, nb, log=False):
    # Find upper and lower bounds
    lower_bound = min(data)
    upper_bound = max(data) + 1

    # define bins
    if log:
        lower_bound = np.log10(lower_bound) if lower_bound > 0 else 0
        upper_bound = np.log10(upper_bound)
        bins = np.logspace(lower_bound, upper_bound, nb)
    else:
        bins = np.linspace(lower_bound, upper_bound, nb)
        
    # compute the midpoint of each bin
    sx = bins[1:] - np.diff(bins) / 2.0          
    
    bin_width = bins[1:] - np.diff(bins)
    
    # compute the height of each bin
    sy, __ = np.histogram(data, bins = bins, density = True)
    
    # From graph above, vector y holds log-binned values of p_1...p_k
    # For cumulative distribution, we want a vector in which:
    # p_1 = p_2 + p_3 + ... + p_k

    bin_width = sy * np.diff(bins)
    cum_sum = np.cumsum(bin_width[::-1]) #sum the reversed p_k distribution

    return sx, cum_sum[::-1] # return the reverse of the cumulative sum


def compare_distances(df, distances):
    print('Calculating self-similiarity and Ideological similiarity...')
    authentic_df = df[df['authentic'] == 1]

    user_pairs = dict()

    for i, row in authentic_df.iterrows():
        user = row['userid']
        rid = row['rid']

        user_pairs.setdefault(user, list())
        user_pairs[user].append(rid)

    valid = [pair for pair in user_pairs.values() if len(pair) > 1]

    distance_compare = dict()

    distance_compare.setdefault('self', list())
    distance_compare.setdefault('average', list())
    distance_compare.setdefault('all', dict())

    for self1, self2 in valid:
        # find true view:
        for i, row in authentic_df.loc[[self1, self2]].iterrows():
            if row['true_view'] == 1:
                ideo = row['position']
                topic = row['topic']
                primary = row['rid']

        compare = authentic_df[(authentic_df['position'] == ideo) & 
                               (authentic_df['topic'] == topic) & 
                               (authentic_df['true_view'] == 1)]['rid'].tolist()

        compare.remove(primary)
        self_distance = distances[self1][self2]
        all_distances = [distances[primary][other] for other in compare]    

        # save to dict
        distance_compare['self'].append(self_distance)
        distance_compare['average'].append(np.mean(all_distances))
        distance_compare['all'][self1] = all_distances

    return distance_compare


def plot_distances(distance_compare, outfile='similiarity.pdf'):
    result = sp.ttest_ind(distance_compare['self'], distance_compare['average']).pvalue
    if result < 0.05:
        print('\tDistributions are significantly different with p=%.5f' % result)
    else:
        print('\tDistributions not significantly different with p=%.3f' % result)

    x, y = get_cumulative(distance_compare['self'], nb=50, log=False)
    y = [1 - num for num in y]
    plt.plot(x, y, label='Self similarity')

    x, y = get_cumulative(distance_compare['average'], nb=50, log=False)
    y = [1 - num for num in y]
    plt.plot(x, y, label='Ideological similiarity')

    plt.xlabel('Distance')
    plt.ylabel('Cumulative Distribution')
    plt.legend()
    plt.savefig(outfile, bbox_inches='tight')
    plt.close()
    print('\tPlotted distributions saved to %s.' % (plot_path + outfile))


def plot_feature_dist(df, feature, feature_label):
    print('Plotting distributions for feature %s.' % feature_label)
    outfile = '%s_distribution.pdf' % feature

    authentic = df[df['authentic'] == 1][feature]
    inauthentic = df[df['authentic'] == 0][feature]

    x, y = get_cumulative(authentic, nb=50, log=False)
    y = [1 - num for num in y]
    plt.plot(x, y, label='authentic')

    x, y = get_cumulative(inauthentic, nb=50, log=False)
    y = [1 - num for num in y]
    plt.plot(x, y, label='inauthentic')

    plt.xlabel(feature_label)
    plt.ylabel('Cumulative Distribution')
    plt.legend()
    plt.savefig(outfile, bbox_inches='tight')
    plt.close()
    print('\tPlotted distributions saved to %s.' % (plot_path + outfile))


def get_confusion(y, y_hat):
    accuracy = len(np.where(y == y_hat)[0]) / len(y_hat)

    true_pos = len(np.where( (y == y_hat) & (y == 1. ))[0]) / len(y == 1.)
    false_pos = len(np.where ((y != y_hat) & (y == 0. ))[0]) / len(y == 1. )
    
    true_neg = len(np.where( (y == y_hat) & (y == 0. ))[0]) / len(y == 0. )

    false_neg = len(np.where( (y != y_hat) & (y == 1. ))[0]) / len(y == 0. )

    confusion = pd.DataFrame([[true_pos, false_pos], [false_neg, true_neg]], 
                            columns = ['actual true', 'actual false'], 
                            index = ['predicted true', 'predicted false'])
    
    return accuracy, confusion


def init_regression(df):
    print('\nPreparing to run regressions.')
    features = df.rename(columns={'giant component' : 'giant_component',
                            'k avg' : 'k_avg',
                            'k std' : 'k_std' })
    features = pd.DataFrame(scaler.fit_transform(features[model3]), columns=model3)
    features.insert(0, 'y', df['authentic'])
    features['const'] = [1. for val in range(len(features))]

    baseline = len(features[features['y'] == 1]) / len(features)
    print('Baseline (if we guess all are authentic) is %.2f%%\n' %baseline)

    N = len(features)
    train_index = random.sample(range(N), int(N * .8))
    test_index = [val for val in range(N) if val not in train_index]

    train = features.loc[train_index]
    test = features.loc[test_index]

    return train, test


def run_regressions(train, test):

    y = test['y']  # true values in test set
    results = dict()

    for model_num, formula in formulas.items():
        results.setdefault(model_num, dict())

        print('Running Model %s: %s' % (model_num, formula))
        result = sm.formula.glm(formula,
                            family=sm.families.Binomial(),
                            data=train).fit()

        y_hat = result.predict(test).round()
        accuracy, confusion = get_confusion(y, y_hat)

        print('\tModel %s has %.3f%% accuracy.' % (model_num, accuracy))

        results[model_num]['full'] = result
        results[model_num]['accuracy'] = accuracy
        results[model_num]['confusion'] = confusion

    print('***Significant features***')
    for i, result_dict in results.items():
        result = result_dict['full']

        p_vals = dict(result.pvalues)
        print('\nModel %s' % i)
        for item, val in p_vals.items():
            if val < 0.05 and item != 'Intercept':
                print('   ', item, '%.5f' %val)

    return results


def plot(results, labels=model3, models=[1, 2, 3]):
    outfile = 'regression_model' + '_'.join(list(map(str, models))) + '.pdf'

    y = [-i for i, label in enumerate(labels)]

    for i, result_dict in results.items():

        result = result_dict['full']

        if i in models:
            coeffs = list(dict(result.params).values())[1:]
            se = list(dict(result.bse).values())[1:]
            error = [1.96 * x for x in se]

            if i == 1:
                y_vals = y[:2]
            elif i == 2:
                y_vals = y[2:]
            else:
                y_vals = y

            plt.errorbar(coeffs, y_vals, xerr = error, fmt='o', capsize =  5, label = 'Model %s' %i)

    plt.axvline(x=0, linestyle='--', color='grey', alpha=0.5)
    plt.yticks(y, labels)
    plt.xticks(np.arange(-5, 6, 1))
    plt.legend(bbox_to_anchor=(1, 1))
    plt.savefig(outfile, bbox_inches='tight')
    plt.close()
    if len(models) > 1:
        model_output = ','.join(list(map(str, models)))

        print('\tModels ' + model_output + ' saved to %s.' % (plot_path + outfile))
    else:
        print('\tModel%s saved to %s.' % (models[0], plot_path + outfile))


def write_results(results):
    with open('regression_summaries.tex', 'w') as fp:
        # begin output
        tex = ['\\documentclass[letterpaper]{article}',
               '\\usepackage[utf8]{inputenc}',
               '\\usepackage{booktabs}\n\n'
               '\\title{Logistic Regression Results}',
                '\\author{Sarah Shugars}',
                '\\date{\\today}\n\n',
               '\\begin{document}\n',
               '\\maketitle\n\n',
               '\\end{document}']

        for item in tex[:-1]:
            fp.write(item + '\n')

        for i, result_dict in results.items():
            result = result_dict['full']
            accuracy = result_dict['accuracy']
            confusion = result_dict['confusion']
            
            fp.write('Results: Model %s (%.3f\\%% accuracy).\n' %(i, accuracy))
            fp.write(result.summary().as_latex())
            
            fp.write('\\vspace{.5em}\n')
            fp.write(confusion.to_latex())
            
            fp.write('\n\\vspace{2em}\n')

        fp.write(tex[-1])
    print('All regression summaries written to file.')


# ---------- Main Function -------------- #
def main():

    print('Loading data.')

    # load distance calculations
    distances = pd.read_csv('distances.txt', sep='\t', index_col=0)
    distances = distances.rename(columns=dict((val, int(val)) for val in distances.columns))

    # general user info
    df = pd.read_csv('yougov_data.txt', sep='\t', index_col=0)

    # change to plotting path
    os.chdir(plot_path)
    distance_compare = compare_distances(df, distances)
    plot_distances(distance_compare)

    plot_feature_dist(df, 'word_count', 'Word Count')
    plot_feature_dist(df, 'FK', 'Flesch-Kincaid Readability')

    # regressions
    train, test = init_regression(df)
    results = run_regressions(train, test)

    print('\nPlotting results.')
    plot(results, labels=model3, models=[1, 2])
    plot(results, labels=model3, models=[3])

    # change to data path
    os.chdir(path)
    write_results(results)


main()