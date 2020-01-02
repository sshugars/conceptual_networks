import os
import json
import datetime
import pandas as pd

import scoring

################# Preliminaries #################

path = '../data/MTurk/'
os.chdir(path)

survey_file = "raw/raw_survey_responses.tsv"
activity_file = "raw/raw_user_data.json" 


# entries before start time are invalid (eg, tests by developers)
start_time = datetime.datetime(2017, 6, 6, 18, 50, 0)

# There were more developer/researcher tests after launch
test_users = ['167739','167753', '167754', '167976', '168202', '168346', '168423', 
              '168543', '168748', '168818', '168829']

topics = {
    'Do you think it is the responsibility of the federal government to make sure all Americans have health care coverage, or that that this is not the responsibility of the federal government?' :' healthcare',
    "Do you think it is the responsibility of the federal government to make sure all Americans have health care coverage?" : "healthcare",
    "Do you think abortions should be legal under any circumstances, legal only under certain circumstances, or never legal under any circumstances?" : "abortion", 
    "If you had to choose, which traits are more important for a child to have: obedience and good manners, or independence and curiosity?": "childrearing" 
}

################# Functions #################

def get_datetime(date_str):
    date, time = date_str.split()
    year, month, day = map(int, date.split('-'))
    hour, minute, second = map(int, time.split(':'))
    
    timestamp = datetime.datetime(year, month, day, hour, minute, second) 
    
    return timestamp

def get_survey(survey_file):

    with open(survey_file, 'r', encoding='utf-16le') as fp:
        raw_responses = fp.read().splitlines()
        
    responses_dict = dict()

    #note that rows 0-2 have header information
    # we use row 1 as our header titles
    for i, line in enumerate(raw_responses):
        line = line.split('\t')
        
        # move uid for ease
        uid = line[-2]
        line.remove(uid)
        line.insert(0,uid)
        
        if i == 1:
            header = line
            
            # add header feilds for the items we will calculate
            scores = ['Harm (MF)', 'Fairness (MF)', 'Ingroup (MF)', 'Authority (MF)', 'Purity (MF)',
                    'Progressivism (MF)', 'Extroversion (Big 5)', 'Agreeableness (Big 5)', 'Conscientiousness (Big 5)',
                    'Neuroticism (Big 5)', 'Openness (Big 5)', 'Deliberation', 'Knowledge', 'Ideology']
            
            for value in scores[::-1]:
                header.insert(38, value)
            
            for item in header:
                responses_dict.setdefault(item, list())
        
        # everything else contains data
        elif i > 2:
            # check if this was completed after the study launched
            end_time = get_datetime(line[1])
            finished = line[7]
            
            if end_time > start_time and finished == 'True' and uid not in test_users:
                
                # calculate summary values
                line = scoring.calc_scores(line)

                for k, v in zip(header, line):
                    responses_dict[k].append(v)
                
    responses = pd.DataFrame(responses_dict)

    return responses

def get_activity_data(activity_file, uids):

    with open(activity_file, 'r') as fp:
        data = json.load(fp)

    activity_dict = dict()

    for entry in data['tests']: 
        user_id = str(entry['id'])

        if len(entry['submissions']) > 0:
            end_time = get_datetime(entry['subjects'][0]['last_ping'])
     
            if end_time > start_time and user_id in uids: 
                activity_dict.setdefault(user_id, dict())

                for sub in entry['submissions']:
                    try:
                        info = sub['val']
                        options = info.keys()

                        if 'topic_order' in options:
                            topics_served = info['topics_served']
                            topic_order = [topics[item] for item in info['topic_order'][:topics_served]]
                            activity_order = info['activity_order']

                            activity_dict[user_id].setdefault('meta', dict())
                            activity_dict[user_id]['meta']['topic_order'] = topic_order
                            activity_dict[user_id]['meta']['activity_order'] = activity_order

                        else: #otherwise topic is stored as number
                            topic_number = info['topic']
                            topic = topic_order[topic_number]
                            activity_dict[user_id].setdefault(topic, dict())

                        if 'essay-content' in options: 
                            essay = info['essay-content']
                            activity_dict[user_id][topic]['essay'] = essay

                        elif 'table' in options:
                            node_list = list()
                            edge_list = list()

                            for edge in info['table']:
                                source = edge['keyword']
                                node_list.append(source)
                                
                                try:
                                    target_id = edge['connections'][0]['endIndex']
                                    edge_list.append((source, target_id))
                                except:
                                    pass

                            node_lookup = dict((index, node) for index, node in enumerate(node_list))

                            final_edge_list = []

                            for edge in edge_list:                    
                                target = node_lookup[edge[1]]
                                final_edge_list.append((edge[0], target))

                            activity_dict[user_id][topic].setdefault('chat', dict())
                            activity_dict[user_id][topic]['chat']['chat_nodes'] = list(node_list)
                            activity_dict[user_id][topic]['chat']['chat_edges'] = final_edge_list

                        elif 'links' in options:
                            edge_list = []
                             
                            for edge in info['links']:
                                source = edge['source']['name']
                                target = edge['target']['name']

                                edge_list.append((source, target))

                            node_list = set() 
                            for item in sub['val']['nodes']:
                                node = item['name']
                                node_list.add(node)

                            activity_dict[user_id][topic].setdefault('viz', dict())
                            
                            activity_dict[user_id][topic]['viz']['viz_nodes'] = list(node_list)
                            activity_dict[user_id][topic]['viz']['viz_edges'] = edge_list
                    except:
                        pass

    # remove any entries for which we retrieved no data
    clean = dict((user, details) for user, details in activity_dict.items() if len(details) > 0)

    return clean

def main():

    print('Processing survey responses...')
    responses = get_survey(survey_file)

    #save uids of users who completed the survey
    uids = list(responses['testId'])


    print('Processing activity data...')
    activity_dict = get_activity_data(activity_file, uids)

    #filter for users who completed the activities
    responses = responses[responses.testId.isin(list(activity_dict.keys()))]

    print('Writing to file...')
    #write processed data to files
    responses.to_csv('survey_responses.txt', sep ='\t', index = False)

    with open('activity_output.json', 'w') as fp:
        fp.write(json.dumps(activity_dict))

    print('All data processed and written to file!')

main()
