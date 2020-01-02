
import numpy as np
import os
import pandas as pd
import itertools as it
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore', category = UserWarning)
warnings.filterwarnings('ignore', category = RuntimeWarning)
from pymer4.models import Lmer


path = '../data/MTurk'
feature_file = 'mturk_features.txt'

personality = [
    'Harm (MF)',
    'Fairness (MF)',
    'Ingroup (MF)',
    'Authority (MF)',
    'Purity (MF)',
    'Progressivism (MF)',
    'Extroversion (Big 5)',
    'Agreeableness (Big 5)',
    'Conscientiousness (Big 5)',
    'Neuroticism (Big 5)',
    'Openness (Big 5)',
    'Deliberation',
    'Knowledge',
    'Ideology'
]

demographics = [
    'age',
    'gender (M)',
    'Race (white NH)',
    'education',
    'income',
    'partyid (R)',
    'religiosity'
]

stats = ['clustering',
         'giant component',
         'disssortativity',
         'k avg',
         'k std',
         'entropy',
         'density']


def get_tvals(measure, features, reverse = False):
    t_matrix = np.zeros((len(measure), len(stats)))
    p_matrix = np.zeros((len(measure), len(stats)))

    method_count = len(set(features['method']))

    for measure_index, net_index in list(it.product(range(len(measure)), range(len(stats)))):
        measure_stat = measure[measure_index]
        net_stat = stats[net_index]

        # create a smaller dataframe

        df = features[['userID', 'topic', 'method', measure_stat, net_stat]]
        df = df.rename(columns={measure_stat: 'measure_stat', net_stat: 'net_stat'})

        # run model
        if method_count > 1:  # if methods to compare
            model = Lmer('measure_stat ~ net_stat  + (1 | topic ) + (1 | method)', data=df)
            model.fit(no_warnings=True, summarize=False)

        else:  # no method comparison
            model = Lmer('measure_stat ~ net_stat  + (1 | topic )', data=df)
            model.fit(no_warnings=True, summarize=False)           

        # get t-vals
        t_val = model.coefs['T-stat']['net_stat']

        if np.isnan(t_val):
            t_val = 0
            print('Warning: no t_val found for method %s, feature %s.\
                Correlation estimated at 0.')

        t_matrix[measure_index][net_index] = t_val

        # get p-val
        p_val = model.coefs['P-val']['net_stat']
        p_matrix[measure_index][net_index] = p_val

    corr = pd.DataFrame(t_matrix.T, index=stats, columns=measure)

    return corr


def method_check(methods, options):
    methods = [item.strip().lower() for item in methods.split(',')]

    valid = [method for method in methods if method in options]
    invalid = [method for method in methods if method not in options]

    if 'all' in valid:
        valid = ['all']
        invalid = list()
        return valid, invalid

    else:
        return valid, invalid


def get_methods():
    options = ['all', 'chat', 'viz', 'noun_parse', 'grammar_parse']

    methods = input('Please enter the methods you would like to include seperated by a comma.\nChoices are: %s\n' % (', '.join(options)))

    valid, invalid = method_check(methods, options)

    while invalid:
        print('Invalid input "%s" found.' % ', '.join(invalid))
        print('Valid input "%s" saved.' % ', '.join(valid))

        methods = input('Hit "enter" to proceed with saved methods or enter additional methods seperated by a comma.\n\
        Remaining choices are: %s\n'  % (', '.join([opt for opt in options if opt not in valid])))

        valid, invalid = method_check(methods, options)

    if valid == ['all'] and methods != 'all':
        print('All methods will be considered. Invalid input ignored.\n')    
    else:
        if valid == ['all']:
            valid = options[1:]

        print('Including observations from methods: %s\n' % ', '.join(valid))

    return valid


def main():
    os.chdir(path)
    features = pd.read_csv(feature_file, sep='\t')

    # filter for methods of interest
    methods = get_methods()
    features = features[features.method.isin(methods)]

    print('%s observations found' % len(features))

    measures = personality + demographics

    print('Estimating pairwise multi-level models between %s personality/demographic measures and %s network statistics.' % (len(measures), len(stats)))

    corr = get_tvals(measures, features)

    if len(methods) == 4:
        outfile = 'estimated_corr.txt'
    else:
        outfile = 'estimated_corr_%s.txt' % '_'.join(methods)

    corr.to_csv(outfile)

    print('All correlations calculated and saved to file.')


main()
