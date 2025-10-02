# Language model
import string
import numpy as np
import itertools as it
import spacy
import gensim
from gensim.models import KeyedVectors
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups

print('Importing language model. This will take a few minutes.')

lookups = Lookups()
lemmatizer = Lemmatizer(lookups)
nlp = spacy.load('en_core_web_sm')
model = gensim.models.KeyedVectors.load_word2vec_format('~/nltk_data/models/GoogleNews-vectors-negative300.bin.gz', binary=True)

ignore = ['punct', 'sym', 'det', 'aux', 'prep', 'advmod', 'intj', 'mark']
stop = ['-PRON-', '\'s', 'i.e.'] + [char for char in string.ascii_letters + string.punctuation]


noun_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'WP', 'WP$']
# More info on tags at https://www.clips.uantwerpen.be/pages/mbsp-tags

def get_clusters(nodes):
    similiarities = dict()

    for word1, word2 in it.combinations(nodes, 2):
        sim = model.similarity(word1, word2)
        similiarities.setdefault(word1, dict())
        similiarities.setdefault(word2, dict())

        if sim > 0.5:
            similiarities[word1][word2] = sim
            similiarities[word2][word1] = sim


    clusters = np.zeros(len(nodes))

    k = 1
    nodes = list(nodes)

    for word1, sim_list in similiarities.items():
        word1_index = nodes.index(word1)

        if clusters[word1_index] == 0:  # if we haven't already assigned a cluster
            sim_words1 = list(sim_list.keys())
            clusters[word1_index] = k

            for word2 in sim_words1:
                sim_words2 = list(similiarities[word2].keys())

                if sorted(sim_words1 + [word1]) == sorted(sim_words2 + [word2]):
                    word2_index = nodes.index(word2)

                    clusters[word2_index] = k

            k += 1
                        
    return clusters

def get_merge(clusters, nodes):
    k = int(max(clusters))

    merge = dict()

    for clust in range(1, k +1):
        word_index = np.where(clusters == clust)[0]

        if len(word_index) > 1: 
            clust_name = list(nodes)[word_index[0]]

            for index in word_index:
                word = list(nodes)[index]
                merge[word] = clust_name
            
    return merge


def get_final(edges, weights, merge):
    final_edges = list()
    final_weights = list()

    for i, (word1, word2) in enumerate(edges):

        #if this is a merge word
        if word1 in merge.keys():
            word1 = merge[word1]

        if word2 in merge.keys():
            word2 = merge[word2]

        #if these are still seperate nodes
        if word1 !=  word2:
            
            final_edges.append([lemmatizer.lookup(word1).lower(), lemmatizer.lookup(word2).lower()])
            final_weights.append(weights[i])

    return final_edges, final_weights


def parse_sentence(doc, nodes, edges, weights, replace, i):
    # get positive version of text
    clean = nlp(' '.join([word.strip() for word in str(doc).split()]))
    pos = nlp(' '.join([token.text for token in clean if token.dep_ != 'neg']))
    neg_parents = [(token.head).text for token in clean if token.dep_ == 'neg']

    remove = set(stop)
    child_parent = dict()
    parent_child = dict()

    word_order = {token: i + j for (j, token) in enumerate(pos)}
    i += len(pos)

    # get parent-child relations
    for token in pos:
        child = token.text
        parent = (token.head).text

        child_index = word_order[token]
        if child_index in replace:
            child = replace[child_index]

        parent_index = word_order[token.head]
        if parent_index in replace:
            parent = replace[parent_index]

        child_parent.setdefault(child, list())
        child_parent[child].append(parent)

        parent_child.setdefault(parent, list())
        parent_child[parent].append(child)

        # keep list of tokens to get rid of
        if token.dep_ in ignore or token.is_stop or child in stop:
            remove.add(child)
            remove.add(token.text)

        # remove out of vocab words
        elif token.text not in model.vocab:
            remove.add(child)
            remove.add(token.text)

    # get node list
    new_nodes = set([p for p in parent_child.keys() if p not in remove] + [c for c in child_parent.keys() if c not in remove])
    nodes = nodes.union(new_nodes)

    # build edge list
    for parent, children in parent_child.items():

        if parent in neg_parents:
            weight = -1
        else:
            weight = 1

        if parent not in remove:
            pairs = [(parent, child) for child in children if child not in remove]

            for pair in pairs:
                if pair[0] != pair[1]:
                    pair = sorted(pair)

                    if pair not in edges:
                        edges.append(pair)
                        weights.append(weight)
                    else:
                        pair_index = edges.index(pair)
                        weights[pair_index] += weight

        else:
            if parent in child_parent:
                keep = [child for child in children if child not in remove] + [parent 
                                                                           for parent in child_parent[parent] 
                                                                           if parent not in remove]
            else:
                keep = [child for child in children if child not in remove] 
            
            pairs = [item for item in it.combinations(keep, 2)]
            

            for pair in pairs:
                if pair[0] != pair[1]:
                    pair = sorted(pair)
                    
                    if pair not in edges:
                        edges.append(pair)
                        weights.append(weight)
                    else:
                        pair_index = edges.index(pair)
                        weights[pair_index] += weight
    
    return nodes, edges, weights, i

def get_replacements(doc):
    ### change format of replace so we can replace parents, too
    
    last_sub = '-PRON-'
    rep_list = list()

    replace = dict()

    for token in doc:
        if token.pos_ == 'PRON':
            rep_list.append(token.text.lower())
        if token.dep_ == 'poss':
            rep_list.append(token.text.lower())

    clean = nlp(' '.join([word.strip() for word in str(doc).split()]))
    pos = nlp(' '.join([token.text for token in clean if token.dep_ != 'neg']))
    
    #identify which words a word refers back to
    for i, token in enumerate(pos):
        if token.dep_ == 'nsubj' and token.pos_ != 'PRON':
            last_sub = token.text.lower() #.lemma_
        if token.dep_ == 'pobj' and token.pos_ != 'PRON':
            last_sub = token.text.lower() #.lemma_

        
        if token.text in rep_list:
            if token.pos_ == 'PRON' and token.dep_ != 'nsubjpass':
                replace[i] = last_sub
            elif token.pos_ == 'PRON' and token.dep_ == 'nsubjpass':
                replace[i] = '-PRON-'
                
            elif token.dep_ == 'poss':
                replace[i] = '-PRON-'
            else:
                replace[i] = token.text #replace with self if not replace condition
                
    return replace


def grammar_parse(text):
    edges = list()
    weights = list()
    nodes = set()
    
    text = text.replace('.', '. ')
    
    doc = nlp(text.lower())
    
    replace = get_replacements(doc)
    i = 0
    
    for sent in doc.sents:
        nodes, edges, weights, i = parse_sentence(sent, nodes, edges, weights, replace, i)

    if nodes:
        clusters = get_clusters(nodes)

        # merge nodes that are the same
        merge = get_merge(clusters, nodes)    
        final_edges, final_weights = get_final(edges, weights, merge)

        edges = [(node1, node2, {'weight' : weight}) for [node1, node2], weight in 
                         zip(final_edges, final_weights)]
    else:
        edges = list()
    
    network = {'nodes' : nodes,
               'edges' : edges}
    
    
    return network



def noun_parse(text, window=10):
    text = text.replace('.', '. ')
    doc = nlp(text.lower())

    edges = list()

    for sent in doc.sents:
        node_position = dict()

        for i, token in enumerate(sent):
            if token.pos_ == 'NOUN' or token.tag_ in noun_tags:
                node_position[i] = token.text

        # get edges
        positions = list(node_position.keys())

        for position in positions:
            neighbors = [position + i for i in range(1, window + 1) if position + i in positions]
            neighbors += [position - i for i in range(1, window + 1) if position - i in positions]

            for neighbor in neighbors:
                node1 = node_position[position]
                node2 = node_position[neighbor]

                edges.append(sorted([node1, node2]))

    nodes = list(set([node for edge in edges for node in edge]))

    network = {'nodes': nodes,
               'edges': edges}

    return network