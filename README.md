# conceptual_networks
 Replication material for _The Structure of Reasoning: Measuring Justification and Preferences in Text_. . Sarah Shugars _(working paper)_.  Documentation for this paper is sorted into three folders:

* code/
Contains all code for cleaning, analyzing and visualizing data.

* data/
This paper contains human subject data. In order to maintain subjects' privacy, this folder only included post-processed aggregated data. Please contact me if you are interested in accessing the original datasets used.

* figs/
Contains all figures used within the paper.


# Included scripts
**parse.py**
	Primary language model for inferring conceptual networks from text.  Use as follows:
	
	```
	import parse
	network = grammar_parse(text)
	```
	
	Takes: text, a string
	
	Returns: network, a dictionary with keys 'nodes' and 'edges'.
	
	
**netstats.py**
	Calculates network statistics for a network. Use as follows:
	
	```
	import netstats
	stats = network_stats(G)
	```
	
	Takes: G, a networkx object
	
	Returns: stats, a dictionary of { stat_name : stat_value}

### Scripts for MTurk dataset
**mturk_process_raw.py**

**scoring.py**


**mturk_get_features.py**

**mturk_get_corr.py**

**mturk_visualizations.py**

### Scripts for YouGov dataset

**yougov_process_raw.py**

**yougov_analysis.py**