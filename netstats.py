import json
import scipy.stats as sp
import numpy as np
import itertools as it
import networkx as nx
import warnings
warnings.filterwarnings('ignore')

# Function for calculating network stats
def network_stats(G):

    node_count = len(G)
    
    edge_count = len(G.edges())
    density = (2 * edge_count) / (node_count * (node_count - 1))
    clustering = np.mean(list(nx.clustering(G).values()))   
    
    degree_dist = list(dict(G.degree()).values())
    k_avg = np.mean(degree_dist)
    k_std = np.std(degree_dist, ddof=1)    
    
    giant_component = max(nx.connected_components(G))
    giant_component_percent =  float(len(giant_component)) / float(node_count)

    if min(degree_dist) < 1:
        adjust = np.abs(min(degree_dist)) + 1
    else:
        adjust = 0

    reweighted_dist = [val + adjust for val in degree_dist]

    normed_dist = [reweighted_dist.count(val) / node_count for val in range(1, node_count + 1)]
    entropy = sp.entropy(normed_dist)

    max_ent_dis = list(range(1, node_count + 1))
    max_ent = sp.entropy(max_ent_dis)

    entropy = entropy / max_ent
        
    if k_std == 0: #if degrees equal
        assortativity = 1
    else:
        assortativity = nx.degree_pearson_correlation_coefficient(G)

    if np.isnan(assortativity):
        assortativity = 0

    disassortativity = assortativity * -1


    stats = dict((('node_count', node_count),
                  ('edge_count', edge_count),
                  ('clustering', clustering),
                  ('giant component', giant_component_percent),
                  ('disssortativity', disassortativity),
                  ('k avg', k_avg),
                  ('k std', k_std),
                  ('entropy', entropy),
                  ('density', density)
                 )) 
    
    
    return stats