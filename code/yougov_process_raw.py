import os
import pandas as pd
import pyreadstat
import textstat
import networkx as nx
import json
import netrd
import numpy as np
import itertools as it
import parse
import netstats

dist_obj = netrd.distance.PortraitDivergence()

path = '../data/YouGov/'
os.chdir(path)

coded_file = 'raw/coded.csv'
raw_file = 'raw/HFPO0003_WTS.sav'

lib_qs = ['Q14a', 'Q14b', 'Q14c']
con_qs = ['Q15a', 'Q15b', 'Q15c']
null_response = '__NA__'

topics = {'a': 'abortion',
          'b': 'min_wage',
          'c': 'defense'}

positions = {'14': 'liberal',
             '15': 'conservative'}

ideology = {'1': 'liberal',
            '0': 'conservative'}

demographics = [
 'gender',  # male (1) / female (2)
 'age4',    # under 30 / 30-44 / 45 - 64 / 65 +
 'race4',   # white (1) / black (2) / hispanic (3) / other (4)
 'educ4',   # hs / some college / college grad / post grad
 'pid3',    # dem (1) / rep (2) / ind (3) / other (4)
 'ideo3'    # lib (1) / mod (2) / con (3) / not sure
  ]


def check_view(position, ideology):
    if position == 'liberal' and ideology == 1.0:
        return True
    elif position == 'conservative' and ideology == 3.0:
        return True
    else:
        return False


def get_network(network):
    G = nx.Graph()
    G.add_edges_from(network['edges'])

    for node in network['nodes']:
        G.add_node(node)

    return G


def get_unique_text(all_data):
    unique_data = list()

    for i, row in all_data.iterrows():
        row = dict(row)

        # find out which question they answered
        answered = [key for key, val in row.items() if key in lib_qs + con_qs and val != null_response]

        if answered:
            topic = topics[answered[0][-1]]

            for q in answered:
                pos = positions[q[1:-1]]

                new_data = [str(int(row['caseid'])), topic, pos] + [row[q]] + \
                    [row[demo] for demo in demographics]

                unique_data.append(new_data)

    header = ['userid', 'topic', 'position', 'text'] + demographics
    clean_df = pd.DataFrame(unique_data, columns=header)
    clean_df = clean_df.rename(columns={'ideo3': 'ideology'})

    # add column indicating whether subject holds this view
    true_view = [1 if check_view(position, ideology) else 0
                 for position, ideology in
                 zip(clean_df['position'], clean_df['ideology'])]

    clean_df['true_view'] = true_view

    # add unique row identifier
    rid = [i for i in range(len(clean_df))]
    clean_df.insert(loc=0, column='rid', value=rid)

    return(clean_df)


def get_features(df):

    # Calculate text features for each line
    features = list()
    skipped = dict()
    networks = dict()

    print('Constructing networks and calculating features...')

    for i, text in enumerate(df['text']):

        if i % 500 == 0 and i != 0:
            progress = (i / len(df)) * 100
            print('   %s%% of texts processed...' % int(progress))

        network = parse.grammar_parse(text)

        # if we have a network
        if len(network['nodes']) > 1 and len(network['edges']) > 0:
            network['nodes'] = list(network['nodes']) # make JSON serializable

            G = get_network(network)

            # get network stats
            stats = netstats.network_stats(G)

            # add coarse features
            stats['word_count'] = len(text.split())
            stats['FK'] = textstat.flesch_kincaid_grade(text)

            # save networkx object
            networks[i] = G

            # save data to features dict
            features.append([i] + list(stats.values()))

        # save skipped texts
        else:
            skipped[i] = text

    header = ['rid'] + list(stats.keys())
    feature_df = pd.DataFrame(features, columns=header)

    print('All texts processed.')

    return feature_df, networks


def reindex(df, networks):
    # reindex for entries with networks
    new_index = dict((old, new) for new, old in enumerate(networks.keys()))
    df['rid'] = df.rid.map(new_index)

    # networks
    final_networks = dict((new_index[old], details) for old, details in networks.items())

    return df, final_networks


def get_pairs(df):
    # restrict networks to those who are trying
    valid_pairs = dict()

    for topic in set(df['topic']):
        ontopic = df[(df['topic'] == topic) & (df['authentic'] == 1)]['rid'].tolist()

        valid_pairs[topic] = ontopic

    return valid_pairs


def get_distances(valid_pairs, networks):
    # Calculate distances
    N = np.sum([len(rids) for rids in valid_pairs.values()])
    distances = np.empty((len(networks), len(networks)))
    distances.fill(np.nan)
    combs = int((N * (N - 1)) / 2)

    print('Calculating %s pairwise distances. This will take about 10 minutes.' % combs)

    for topic, rids in valid_pairs.items():
        topic_combs = int((len(rids) * (len(rids) - 1)) / 2)
        print('   Comparing networks from topic "%s" (%s pairs).' %(topic, topic_combs))

        for i, j in it.combinations(rids, 2):

            # network i
            G = networks[i]

            # network j
            H = networks[j]

            # calculate distance
            dist = dist_obj.dist(G, H)

            # save distance
            distances[i][j] = dist
            distances[j][i] = dist

    distance_df = pd.DataFrame(distances)

    return distance_df

    print('All pairwise distances calculated.')


def main():
    print('Loading data...')
    # load raw data
    df, meta = pyreadstat.read_sav(raw_file)
    raw_df = df[['caseid'] + lib_qs + con_qs + demographics]

    # give each text response its own row
    df = get_unique_text(raw_df)

    # load coded data
    data = pd.read_csv(coded_file, index_col=0, sep='\t')
    data['userid'] = [str(uid) for uid in data['userid']]

    # keep just the columns we need
    data = data[['userid', 'topic', 'position', 'authentic']]

    # merge data
    all_data = data.merge(df, on=['userid', 'topic', 'position'], how='inner')
    print('%s observations loaded.' % len(all_data))

    features, networks = get_features(all_data)

    # merge features into existing df
    merged_df = all_data.merge(features, on='rid', how='inner')

    # reindex to make life easier
    df, networks = reindex(merged_df, networks)

    # Write data to file
    print('Writing features and survey data to file.')
    df.to_csv('yougov_data.txt', sep='\t')

    # calculate distances
    valid_pairs = get_pairs(df)
    distance_df = get_distances(valid_pairs, networks)

    distance_df.to_csv('distances.txt', sep='\t')

    print('Distance calculations saved to file.')


main()
