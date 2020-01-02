import os
import json
import pandas as pd
import networkx as nx

print('Importing language model. This will take a few minutes.')
import netstats
import parse

path = '../data/MTurk'
os.chdir(path)

activity_file = 'activity_output.json'
survey_file = 'survey_responses.txt'

# add survey details
demographics = {
    'testId': 'userID',
    'What is your age?': 'age',
    'What is your gender? - Selected Choice': 'gender (M)',
    'What is your race? (Check all that apply) - Selected Choice': 'Race (white NH)',
    'What is the highest level of education you have completed?': 'education',
    'What is your annual household income?': 'income',
    'Generally speaking, do you usually think of yourself as a Republican, a Democrat, an Independent, or something else?': 'partyid (R)',
    'Aside from weddings and funerals, how often do you attend religious services?': 'religiosity'
}

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

survey_keep = list(demographics.keys()) + personality

age_ranges = {
    '18 - 24': 0,
    '25 - 34': 1,
    '35 - 44': 2,
    '45 - 54': 3,
    '55 - 64': 4
}

gender_map = {
    'Female': 0,
    'Male': 1
}

education_map = {
    'Less than high school': 0,
    'High school graduate': 1,
    'Some college': 2,
    '2 year degree': 3,
    '4 year degree': 4,
    'Professional degree': 5
}

income_map = {
    '$10,000 - $19,999': 0,
    '$100,000 - $149,999': 1,
    '$20,000 - $29,999': 2,
    '$30,000 - $39,999': 3,
    '$40,000 - $49,999': 4,
    '$50,000 - $59,999': 5,
    '$60,000 - $69,999': 6,
    '$70,000 - $79,999': 7,
    '$80,000 - $89,999': 8,
    '$90,000 - $99,999': 9,
    'Less than $10,000': 10,
    'More than $150,000': 11
}

party_map = {
    'Democrat': 0,
    'Independent': 0.5,
    'No preference': 0.5,
    'Other': 0.5,
    'Republican': 1
}

religious_map = {
    'Don\'t know/prefer not to say': 0,
    'Never': 1,
    'Seldom': 2,
    'A few times a year': 3,
    'Once or twice a month': 4,
    'Once a week': 5
}

remapping = {
    'age': age_ranges,
    'gender (M)': gender_map,
    'education': education_map,
    'income': income_map,
    'partyid (R)': party_map,
    'religiosity': religious_map
}


def remove_none(nodes, edges):
    nodes = [item for item in nodes if item != None]
    edges = [edge for edge in edges if edge[0] != None and edge[1] != None]
    
    return nodes, edges


def get_network_stats(nodes, edges):

    nodes, edges = remove_none(nodes, edges)

    if len(nodes) > 1 and len(edges) > 0:
        G = nx.Graph()

        G.add_edges_from(edges)

        for node in nodes:
            G.add_node(node)

        stats = netstats.network_stats(G)

    else:
        stats = dict()

    return stats


def process_networks(activity_file):
    with open(activity_file, 'r') as fp:
        data = json.loads(fp.read())

    info = list()

    print('Parsing all user networks...')

    for user, details in data.items():
        topics = details['meta']['topic_order']
        essay_order = details['meta']['activity_order'].index('essay')  # 0 - 2

        for topic in topics:
            topic_order = topics.index(topic)  # 0 - 1

            # Essay methods
            try:
                essay = details[topic]['essay']

                # grammar parse
                network = parse.grammar_parse(essay)
                stats = get_network_stats(network['nodes'], network['edges'])
                
                if len(stats) > 0:
                    user_info = [int(user), 'grammar_parse', essay_order, topic, topic_order] + list(stats.values())
                    info.append(user_info)

                # noun co-occurance
                network = parse.noun_parse(essay)
                stats = get_network_stats(network['nodes'], network['edges'])
                
                if len(stats) > 0:
                    user_info = [int(user), 'noun_parse', essay_order, topic, topic_order] + list(stats.values())
                    info.append(user_info)

            except Exception:
                print('  No essay found for user: %s, topic: %s' %(user, topic))

            #viz method
            try:
                viz_order = details['meta']['activity_order'].index('D3 viz')
                
                viz_edges = details[topic]['viz']['viz_edges']
                viz_nodes = details[topic]['viz']['viz_nodes']
                
                stats = get_network_stats(viz_nodes, viz_edges)

                if len(stats) > 0:
                    user_info = [int(user), 'viz', viz_order, topic, topic_order] + list(stats.values())
                    info.append(user_info)

            except Exception:
                print('  No visualization found for user: %s, topic: %s' %(user, topic))


            # chat
            try:
                chat_order = details['meta']['activity_order'].index('chatbot')
                    
                chat_edges = details[topic]['chat']['chat_edges']
                chat_nodes = details[topic]['chat']['chat_nodes']

                stats = get_network_stats(chat_nodes, chat_edges)

                if len(stats) > 0:
                    user_info = [int(user), 'chat', chat_order, topic, topic_order] + list(stats.values())  
                    info.append(user_info)

            except Exception:
                print('  No chat data found for user: %s, topic: %s' %(user, topic))

    header = ['userID', 'method', 'method order', 'topic', 'topic_order'] + list(stats.keys())
    network_details = pd.DataFrame(info, columns=header)

    print('All users data processed.')
                
    return network_details

def get_survey_responses(survey_file):

    # load all data
    survey = pd.read_csv(survey_file, sep='\t')

    # save hispanic demographic for later
    hispanic = survey['Do you identify as Hispanic or Latino?']

    # get just fields we care about
    survey = survey[survey_keep]
    survey.rename(columns=demographics, inplace=True)

    for key, mapping in remapping.items():
        survey[key] = survey[key].map(mapping)

    # race coding
    race = [1 if i == 'White' and j == 'No' else 0 for i, j in zip(survey['Race (white NH)'], hispanic)]
    survey['Race (white NH)'] = race

    return survey


def main():
    essay_details = process_networks(activity_file)
    survey = get_survey_responses(survey_file)

    user_data = essay_details.merge(survey, on='userID', how='inner')
    user_data.to_csv('mturk_features.txt', sep='\t', index=False)
    print('Calculated features written to file.')


main()
