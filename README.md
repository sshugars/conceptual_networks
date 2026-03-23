# Conceptual Networks
 Replication material for _The Structure of Reasoning: Measuring Justification and Preferences in Text_. Sarah Shugars and Xinfeng Gu _(working paper)_.  Documentation for this paper is sorted into three folders:

* [home] : Contains all code for cleaning, analyzing and visualizing data.

* data/ : Raw data collected from ANES 2016 along with datasets recording several intermediary and final steps of analysis.

* figs/ : Contains all figures used within the paper along with key calculations.


# Included scripts
**1_dataCleaning.ipynb**

    This notebook walks through the steps of:
    1. Loading the raw 2016 ANES data
    2. Cleaning text fields

    Input:
    `data/ANES_2016.csv` : raw data

    Output:
    `data/ANES_2016_CLEANED.txt` : a tab-seperated file with `_clean` fields for every text response. 


**2_HyperparameterTuning.ipynb**

    This notebook examines UMAP and hdbscan hyperparameters. The goal in using these algorithms is to identify clusters of words that substantially represent the same "concept." Different parameters are tried, checked for coherence, and manually inspected.

    Input:
    `data/ANES_2016_CLEANED.txt` : a tab-seperated file with `_clean` fields for every text response. 

    Output:
    No output file. However, hyperparameters determined to result in coherent word clusters are retained for use in `3_NetworkExtraction.ipynb`. 


**3_NetworkExtraction.ipynb**

    This notebook walks through the steps of:
    1. Extracting networks from text
    2. Calculating network statistics

    Note that hyperparamaters used for UMAP and hdbscan are determined through through process in `2_HyperparameterTuning.ipynb`. This notebook also uses the helper function defined in `netstats.py`, described below.

    Input:
    `data/ANES_2016_CLEANED.txt` : a tab-seperated file with `_clean` fields for every text response. 

    Output:
    `data/network_data.csv` : a file with extracted networks (node + edge lists) and network statistics.


**4_Analysis.ipynb**

    This notebook uses networks and network statistics output from `3_NetworkExtraction.ipynb` notebook to conducts the core analyses of this paper:
    * **Analysis 1: Network structure + personality**
    * **Analysis 2: Self-similarity vs. ideological similarity**
    Results are saved for visualizion in `5_Figures.ipynb`

    Input:
    `data/network_data.csv` : a file with extracted networks (node + edge lists) and network statistics.

    Output:
    `data/stats.csv` : Reshaped input data, so every _response_ is an observation. Original data has every _subject_ as an observation.
    `data/corr.txt` : Matrix of pairwise correlations between network measures and personality traits.
    `data/p_vals.txt` : Matrix of p-values associated with pairwise correlations.
    `data/distances.json` : Pairwise distances (Portrait Divergence) between networks.


**5_Figures.ipynb**

    This notebook uses the calculated values from `4_Analysis.ipynb` notebook to visualize the core relationships for this project:
    * **Analysis 1: Network structure + personality**
    * **Analysis 2: Self-similarity vs. ideological similarity**

    Input:
    `data/corr.txt` : Matrix of pairwise correlations between network measures and personality traits.
    `data/p_vals.txt` : Matrix of p-values associated with pairwise correlations.
    `data/distances.json` : Pairwise distances (Portrait Divergence) between networks.

    Output:\
    `figs/corr.png` : Figure 4, Correlations between demographics and network stats.
    `figs/NetSim.png` : Figure 5, Distribution of network distance.
    `figs/NetSim_all_cum.png` : Cumulative distribution, not used in paper.


**netstats.py**
    Helper function to calculate network statistics for an input network. Use as follows:

    ```
    import netstats
    stats = network_stats(G)
    ```

    Takes: G, a networkx object

    Returns: stats, a dictionary of { stat_name : stat_value}
