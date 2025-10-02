import re


orig_names = ["testId", "Start Date","End Date","Response Type","IP Address","Progress","Duration (in seconds)",
             "Finished", "Recorded Date", "Response ID", "Recipient Last Name", "Recipient First Name",
             "Recipient Email","External Data Reference","Location Latitude","Location Longitude","Distribution Channel", "User Language",
             "Do you currently reside in the United States?","What is your age?","What is your gender? - Selected Choice",
             "What is your gender? - Self-identify as - Text", "Do you identify as Hispanic or Latino?", 
             "What is your race? (Check all that apply) - Selected Choice", 
             "What is your race? (Check all that apply) - Self-identify as - Text", "In what state do you currently reside?",
             "In what city or town do you currently reside?","Were you born in the US?","Your country/countries of origin is/are:",
             "In which of the past elections did you vote? (Check all that apply)",
             "What is the highest level of education you have completed?","What is your annual household income?",
             "Thinking about politics these days, how would you describe your own political viewpoint?",
             "Generally speaking, do you usually think of yourself as a Republican, a Democrat, an Independent, or something else?",
             "Who did you vote in the 2016 US Presidential election","Aside from weddings and funerals how often do you attend religious services?","What is your present religion, if any?",
             "Optional: If you have an account on Twitter, please provide your Twitter @ username or handle below. We will only scrape your recent public Twitter posts and profile, and all data will be stored anonymously and encrypted in a secure server.",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone suffered emotionally",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not some people were treated differently than others",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone's action showed love for his or her country",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone showed a lack of respect for authority",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone violated standards of purity and decency",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone was good at math",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone cared for someone weak or vulnerable",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone acted unfairly",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone did something to betray his or her group",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone conformed to the traditions of society",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone did something disgusting",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone was cruel",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone was denied his or her rights",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone showed a lack of loyalty",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not an action caused chaos or disorder",
             "When you decide whether something is right or wrong, to what extent are the following considerations relevant to your thinking? Please rate each statement using a scale from 0 (not at all relevant; this consideration has nothing to do with my judgments of right and wrong) to 5 (extremely relevant; this is one of the most important factors when I judge right and wrong). - Whether or not someone acted in a way that God would approve of",
             "Please read the following sentences and indicate your agreement or disagreement. - Compassion for those who are suffering is the most crucial virtue.",
             "Please read the following sentences and indicate your agreement or disagreement. - When the government makes laws, the number one principle should be ensuring that everyone is treated fairly.",
             "Please read the following sentences and indicate your agreement or disagreement. - I am proud of my country's history.",
             "Please read the following sentences and indicate your agreement or disagreement. - Respect for authority is something all children need to learn.",
             "Please read the following sentences and indicate your agreement or disagreement. - People should not do things that are disgusting, even if no one is harmed.",
             "Please read the following sentences and indicate your agreement or disagreement. - It is better to do good than to do bad.",
             "Please read the following sentences and indicate your agreement or disagreement. - One of the worst things a person could do is hurt a defenseless animal.",
             "Please read the following sentences and indicate your agreement or disagreement. - Justice is the most important requirement for a society.",
             "Please read the following sentences and indicate your agreement or disagreement. - People should be loyal to their family members, even when they have done something wrong.",
             "Please read the following sentences and indicate your agreement or disagreement. - Men and women each have different roles to play in society.",
             "Please read the following sentences and indicate your agreement or disagreement. - I would call some acts wrong on the grounds that they are unnatural.",
             "Please read the following sentences and indicate your agreement or disagreement. - It can never be right to kill a human being.",
             "Please read the following sentences and indicate your agreement or disagreement. - I think it's morally wrong that rich children inherit a lot of money while poor children inherit nothing.",
             "Please read the following sentences and indicate your agreement or disagreement. - It is more important to be a team player than to express oneself.",
             "Please read the following sentences and indicate your agreement or disagreement. - If I were a soldier and disagreed with my commanding officer's orders, I would obey anyway because that is my duty.",
             "Please read the following sentences and indicate your agreement or disagreement. - Chastity is an important and valuable virtue.",
             "I see myself as someone who: - Is talkative",
             "I see myself as someone who: - Tends to find fault with others",
             "I see myself as someone who: - Does a thorough job",
             "I see myself as someone who: - Is depressed, blue",
             "I see myself as someone who: - Is original, comes up with new ideas",
             "I see myself as someone who: - Is reserved",
             "I see myself as someone who: - Is helpful and unselfish with others",
             "I see myself as someone who: - Can be somewhat careless",
             "I see myself as someone who: - Is relaxed, handles stress well",
             "I see myself as someone who: - Is curious about many different things",
             "I see myself as someone who: - Is full of energy",
             "I see myself as someone who: - Starts quarrels with others",
             "I see myself as someone who: - Is a reliable worker",
             "I see myself as someone who: - Can be tense",
             "I see myself as someone who: - Is ingenious, a deep thinker",
             "I see myself as someone who: - Generates a lot of enthusiasm",
             "I see myself as someone who: - Has a forgiving nature",
             "I see myself as someone who: - Tends to be disorganized",
             "I see myself as someone who: - Worries a lot",
             "I see myself as someone who: - Has an active imagination",
             "I see myself as someone who: - Tends to be quiet",
             "I see myself as someone who: - Is generally trusting",
             "I see myself as someone who: - Tends to be lazy",
             "I see myself as someone who: - Is emotionally stable, not easily upset",
             "I see myself as someone who: - Is inventive",
             "I see myself as someone who: - Has an assertive personality",
             "I see myself as someone who: - Can be cold and aloof",
             "I see myself as someone who: - Perseveres until the task is finished",
             "I see myself as someone who: - Can be moody",
             "I see myself as someone who: - Values artistic, aesthetic experiences",
             "I see myself as someone who: - Is sometimes shy, inhibited",
             "I see myself as someone who: - Is considerate and kind to almost everyone",
             "I see myself as someone who: - Does things efficiently",
             "I see myself as someone who: - Remains calm in tense situations",
             "I see myself as someone who: - Prefers work that is routine",
             "I see myself as someone who: - Is outgoing, sociable",
             "I see myself as someone who: - Is sometimes rude to others",
             "I see myself as someone who: - Makes plans and follows through with them",
             "I see myself as someone who: - Gets nervous easily",
             "I see myself as someone who: - Likes to reflect, play with ideas",
             "I see myself as someone who: - Has few artistic interests",
             "I see myself as someone who: - Likes to cooperate with others",
             "I see myself as someone who: - Is easily distracted",
             "I see myself as someone who: - Is sophisticated in art, music, or literature",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - Even people who strongly disagree can make sound decisions if they sit down and talk.",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - Everyday people from different parties can have civil, respectful conversations about politics.",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - The first step in solving our common problems is to discuss them together.",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - Individual leaders make better decisions than groups like committees, more often than not.",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - When we hear claims that are false or misleading, we have a responsibility to speak up and correct them.",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - People who make political claims must always back up their arguments with solid evidence.",
             "Please say how much you agree or disagree with these statements. There are no correct or incorrect responses to these opinion questions. - People should always present logical arguments in support of their views.",
             "Do you happen to know what job or political office is now held by Mike Pence?",
             "Whose responsibility is it to determine if a law is constitutional or not?",
             "How much of a majority is required for the U.S. Senate and House to override a presidential veto?",
             "Do you happen to know which party has the most members in the House of Representatives in Washington?",
             "Would you say that one of the parties is more conservative than the other at the national level? Which party is more conservative?",
             "a.","b.","c.","d.","e.","f.","g.","h.","i.","j.",
             "Should it be possible for a pregnant woman to obtain a legal abortion if the woman wants it for any reason?",
             "Should it be possible for a pregnant woman to obtain a legal abortion if she became pregnant as a result of rape?",
             "Should health insurance be provided through a single national health insurance system run by the government?", 
             "What form of health care or health insurance do you currently have?",
             "In your opinion, who should be most responsible for paying for any person's medical care (including mental health care)?",
             "Independence or respect for elders?", "Obedience or self-reliance?", 
             "To be considerate or to be well-behaved?", "Curiosity or good manners?",
             "subjectId"]

#Pew Keys
conservative = ["Government is almost always wasteful and inefficient", 
               "Government regulation of business usually does more harm than good",
               "Poor people today have it easy because they can get government benefits without doing anything in return",
                "The government today can't afford to do much more to help the poor",
                "Blacks who can't get ahead in this country are mostly responsible for their own condition",
                "Immigrants today are a burden on our country because they take our jobs, housing and health",
                "The best way to ensure peace is through military strength",
                "Most corporations make a fair and reasonable amount of profit",
                "Stricter environmental laws and regulations cost too many jobs and hurt the economy",
                "Homosexuality should be discouraged by society"]


liberal = ["Government often does a better job than people give it credit for",
          "Government regulation of business is necessary to protect the public interest",
           "Poor people have hard lives because government benefits don't go far enough to help them live decently",
           "The government should do more to help needy Americans, even if it means going deeper into debt",
           "Racial discrimination is the main reason why many black people can't get ahead these days",
           "Immigrants today strengthen our country because of their hard work and talents",
           "Good diplomacy is the best way to ensure peace",
           "Business corporations make too much profit",
           "Stricter environmental laws and regulations are worth the cost",
           "Homosexuality should be accepted by society"]


# Gastil keys
gastil = {
        'Strongly agree' : 3,
        'Agree' : 2,
        'Somewhat agree' : 1,
        'Neither agree nor disagree' : 0,
        'Somewhat disagree' : -1,
        'Disagree' : -2,
        'Strongly disagree' : -3
        }

# Big 5 keys
big5dict = {'Can be tense': 'N', 'Generates a lot of enthusiasm': 'E', 'Tends to be disorganized': 'C', 
            'Is sophisticated in art, music, or literature': 'O', 'Is generally trusting': 'A', 
            'Has an assertive personality': 'E', 'Has a forgiving nature': 'A', 
            'Is original, comes up with new ideas': 'O', 'Does things efficiently': 'C', 
            'Perseveres until the task is finished': 'C', 'Is easily distracted': 'C', 
            'Tends to be quiet': 'E', 'Can be moody': 'N', 'Has few artistic interests': 'O', 'Is talkative': 'E', 
            'Is considerate and kind to almost everyone': 'A', 'Can be somewhat careless': 'C', 
            'Is sometimes shy, inhibited': 'E', 'Is relaxed, handles stress well': 'N', 
            'Is outgoing, sociable': 'E', 'Is inventive': 'O', 'Makes plans and follows through with them': 'C', 
            'Likes to cooperate with others': 'A', 'Is ingenious, a deep thinker': 'O', 'Is reserved': 'E', 
            'Is a reliable worker': 'C', 'Is sometimes rude to others': 'A', 'Gets nervous easily': 'N', 
            'Values artistic, aesthetic experiences': 'O', 'Starts quarrels with others': 'A', 
            'Is emotionally stable, not easily upset': 'N', 'Remains calm in tense situations': 'N', 'Worries a lot': 'N', 
            'Is depressed, blue': 'N', 'Is helpful and unselfish with others': 'A', 'Is curious about many different things': 'O', 
            'Likes to reflect, play with ideas': 'O', 'Does a thorough job': 'C', 'Is full of energy': 'E', 
            'Prefers work that is routine': 'O', 'Tends to be lazy': 'C', 'Tends to find fault with others': 'A', 
            'Can be cold and aloof': 'A', 'Has an active imagination': 'O'}

reverse = ["Tends to find fault with others", "Is reserved", "Can be somewhat careless", "Is relaxed, handles stress well",
          "Starts quarrels with others", "Tends to be disorganized", "Tends to be quiet", "Tends to be lazy",
          "Is emotionally stable, not easily upset", "Can be cold and aloof", "Is sometimes shy, inhibited",
          "Remains calm in tense situations", "Prefers work that is routine", "Is sometimes rude to others", 
           "Has few artistic interests", "Is easily distracted"]


big5score = {
    'Strongly agree' : 5,
    'Agree' : 4,
    'Neither agree nor disagree' : 3,
    'Disagree' : 2,
    'Strongly disagree' : 1
}

big5reverse = {
    'Strongly agree' : 1,
    'Agree' : 2,
    'Neither agree nor disagree' : 3,
    'Disagree' : 4,
    'Strongly disagree' : 5
}


#moral foundations key
moraldict = {
    "Whether or not someone suffered emotionally" : 'H',
    "Whether or not someone cared for someone weak or vulnerable" : 'H',
    "Whether or not someone was cruel"  : 'H',
    "Compassion for those who are suffering is the most crucial virtue." : "H",
    "One of the worst things a person could do is hurt a defenseless animal." : "H", 
    "It can never be right to kill a human being." : "H",
    "Whether or not some people were treated differently than others"  : 'F',
    "Whether or not someone acted unfairly"  : 'F',
    "Whether or not someone was denied his or her rights"  : 'F',
    "When the government makes laws, the number one principle should be ensuring that everyone is treated fairly." : 'F',
    "Justice is the most important requirement for a society." : 'F',
    "I think it's morally wrong that rich children inherit a lot of money while poor children inherit nothing." : 'F',
    "Whether or not someone's action showed love for his or her country" : 'I',
    "Whether or not someone did something to betray his or her group" : 'I',
    "Whether or not someone showed a lack of loyalty" : 'I',
    "I am proud of my country's history." : 'I',
    "People should be loyal to their family members, even when they have done something wrong." : 'I',
    "It is more important to be a team player than to express oneself." : 'I',
    "Whether or not someone showed a lack of respect for authority"  : 'A',
    "Whether or not someone conformed to the traditions of society" : 'A',
    "Whether or not an action caused chaos or disorder" : 'A',
    "Respect for authority is something all children need to learn." : 'A',
    "Men and women each have different roles to play in society." : 'A',
    "If I were a soldier and disagreed with my commanding officer's orders, I would obey anyway because that is my duty." : 'A',
    "Whether or not someone violated standards of purity and decency" : 'P',
    "Whether or not someone did something disgusting" : 'P',
    "Whether or not someone acted in a way that God would approve of" : 'P',
    "People should not do things that are disgusting, even if no one is harmed." : 'P',
    "I would call some acts wrong on the grounds that they are unnatural." : 'P',
    "Chastity is an important and valuable virtue." : 'P'
}

moralscore = {
    'Strongly disagree' : 0,
    'Disagree' : 1,
    'Neither agree nor disagree' : 2.5,
    'Agree' : 4,
    'Strongly agree' : 5
}

#helper function to calculate summary scores
def calc_scores(response, verbose = False):
    ##### political ideology (Pew) ####
    ideology = 0
    
    for num in range(126,136):
        if response[num] in conservative:
            ideology += 1
        elif response[num] in liberal:
            ideology -= 1
        elif response[num] == "No Answer":
            ideology += 0
            
    
    #### political knowledge (Delli Carpini)  ####
    knowledge = 0
    
    # what job is held by Mike Pence?
    r = re.compile('vice|vp')
    m = r.search(response[121].lower())

    if m:
        knowledge += 1
    elif response[121] != "":
        if verbose:
            print("User %s: what job is held by Mike Pence? %s " %(response[0], response[121]))
        
    # Who determines if a law is constitutional?
    if response[122] == "Supreme Court":
        knowledge += 1
        
    # majority to override a presidential veto?
    r = re.compile('2/3|third|66%')
    m = r.search(response[123].lower())
    
    if m:
        knowledge += 1   
    elif response[123] != "":
        if verbose:
            print("User %s: how much of a majority is needed to override a presidential veto? %s " %(response[0], response[123]))

   
    #which party has the most members in the House of Representatives?
    r = re.compile('rep|gop')
    m = r.search(response[124].lower())
    if m:
        knowledge += 1
    elif response[124] != "":
        if verbose:
            print("User %s: which party has the most members in the House of Representatives? %s " %(response[0], response[124]))

    
    #which party is more conservative?
    m = r.search(response[125].lower())
    if m:
        knowledge += 1
    elif response[125] != "":
        if verbose:
            print("User %s: which party is more conservative? %s " %(response[0], response[125]))

        
    #adjust for specific users with "invalid" responses
    if response[0] == 165186:
        knowledge += 1 #response "trump circus member"
    elif response[0] == 168795:
        knowledge += 2 #2 responses "R"
    elif response[0] == 168890:
        knowledge += 2 #2 responses "R"
        
    
    ###### Deliberation (Gastil)  ########
    deliberation = 0
    for num in range(114, 121):
        if response[num] != "":
            score = gastil[response[num]]
        
            if num == 117:
                score = score * -1

            deliberation += score

  
    ######## Big 5  ########
    extroversion = 0
    agreeableness = 0
    conscientiousness = 0
    neuroticism = 0
    openness = 0
    
    for num in range(70,114):
        if response[num] != '':
            #determine score
            question = orig_names[num].split('-')[-1].strip()
            if question in reverse:
                score = big5reverse[response[num]]
            else:
                score = big5score[response[num]]

            trait = big5dict[question]

            #determine trait
            if trait == 'E':
                extroversion += score

            elif trait == 'A':
                agreeableness += score   

            elif trait == 'C':
                conscientiousness += score

            elif trait == 'N':
                neuroticism += score

            elif trait == 'O':
                openness += score
    
    ##### moral foundations #####
    harm = 0
    fairness = 0
    ingroup = 0
    authority = 0
    purity = 0
    
    for num in range(38,70):
        try:
            #determine score
            if num < 54: #first panel
                score = int(response[num])
                
            else: #second panel
                score = moralscore[response[num]]

            #determine trait
            question = orig_names[num].split('-')[-1].strip()
            trait = moraldict[question]
            
            if trait == 'H':
                harm += score

            elif trait == 'F':
                fairness += score   

            elif trait == 'I':
                ingroup += score

            elif trait == 'A':
                authority += score

            elif trait == 'P':
                purity += score
                
        except:
            pass

    #final scores
    harm = float(harm) / 6
    fairness = float(fairness) / 6
    ingroup = float(ingroup) / 6
    authority = float(authority) / 6
    purity = float(purity) / 6
    
    progressivism = ((harm + fairness) / 2) - ((ingroup + authority + purity) / 3)
    
    #Update response data
    items = [format(harm, '.2f'), format(fairness, '.2f'), format(ingroup, '.2f'), format(authority, '.2f'), 
            format(purity,'.2f'), format(progressivism, '.2f'), extroversion, agreeableness, conscientiousness, 
                        neuroticism, openness, deliberation, knowledge, ideology]

    for value in items[::-1]:
        response.insert(38, str(value))
        
    return response