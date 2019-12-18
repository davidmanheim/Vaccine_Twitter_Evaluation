import json
import os
import networkx as nx

# Get the data on users, on thread structures, and then scan the full dataset for what fits where, etc.
with open("data\Classified_Users_With_BotOrNot_One_line.json", 'r') as r:
    Users_Classified = json.loads(r.readline()) ## CURRENTLY INCOMPLETE (Now-Running) FOR BOTS!!! (Finished otherwise.)
    r.close()

with open("data\Thread_Tweet_Structure_at_1563435934.7016308.json", 'r') as r:
    TWStruct = json.loads(r.readline())
    r.close()

with open("data\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json",'r') as r:
    VSN_Peeps = json.loads(r.readline())
    r.close()

# Need to Scan all files for tweets mentioning vaccine keywords.
# The relevant fileset is:
from Tweet_File_Analysis_Functions import Scan_Files_With_Function_Filter, Get_FileList_Of_JSON_Files, RelevantTweet,\
    ListAllTweetIDs
List_1 = Get_FileList_Of_JSON_Files(directory='data', prefix='Tweets_by_', contains='back_to_2008')  # From typo in code
List_2 = Get_FileList_Of_JSON_Files(directory='data', prefix='Tweets_by_', contains='back_to_2018')
List_3 = Get_FileList_Of_JSON_Files(directory='data', prefix='tweets_By_ID_at_')
All_Tweet_Files = List_1.copy()
All_Tweet_Files.extend(List_2)
All_Tweet_Files.extend(List_3)


DateRange = ["Jan 01 00:00:00 2018", "Jan 01 00:00:00 2019"] #Sent during 2018.

Vaccine_Terms = ['mmr', 'measles', 'mumps', 'rubella']
MisInfo_Terms = ['autism', 'poison', 'shills', 'pharma', 'mandatory', 'vaers', 'aluminum', 'mercury', 'thimerosal']
HealthEd_Terms = ['vaccine', 'immunocompromise', 'preventable disease', 'rumors', 'debunk', 'expert',
                  "infectious disease", "immunization"]
All_Terms = Vaccine_Terms + MisInfo_Terms + HealthEd_Terms

# Don't redo this:
if not os.path.isfile('data\Tweet_List_Relevant_Dict_List.json'):
    Tweet_List_Relevant_Dict_List = \
        Scan_Files_With_Function_Filter(Filelist=All_Tweet_Files, Filter=RelevantTweet, AggNotList=False, Silent=True,
                                        Termlist=All_Terms, DateRange=DateRange)

    with open('data\Tweet_List_Relevant_Dict_List.json','w+') as f:
        f.write(json.dumps(Tweet_List_Relevant_Dict_List))
        f.close()

with open('data\Tweet_List_Relevant_Dict_List.json','r') as f:
    Tweet_List_Relevant_Dict_List=json.loads(f.readline())
    f.close()

# Just to count the tweets:
if not os.path.isfile('data\Tweet_List_All_Dict_List.json'):
    Tweet_List_All_Dict_List = \
        Scan_Files_With_Function_Filter(Filelist=All_Tweet_Files, Filter=RelevantTweet, AggNotList=False, Silent=True,
                                        Termlist = None, DateRange=DateRange)

    with open('data\Tweet_List_All_Dict_List.json','w+') as f:
        f.write(json.dumps(Tweet_List_All_Dict_List))
        f.close()

#with open('data\Tweet_List_All_Dict_List.json','r') as f:
#    Tweet_List_All_Dict_List=json.loads(f.readline())
#    f.close()

#TotalTweets = 0
#for file in Tweet_List_All_Dict_List:
#    for entry in Tweet_List_All_Dict_List[file]:
#        TotalTweets=TotalTweets+ len(Tweet_List_All_Dict_List[file][entry])
# 1,017,176 total tweets.


#Get list of tweet IDs, not dict of counts
#Actually, just make the file. It will be huge. Oh Well.
if not os.path.isfile('data/All_Keywords_Relevant_Tweets_from_Initial_Dataset.json'):# Don't redo it
    from itertools import islice
    with open('data/All_Keywords_Relevant_Tweets_from_Initial_Dataset.json', 'a') as f:
        for key in Tweet_List_Relevant_Dict_List.keys():
            if 'true' in Tweet_List_Relevant_Dict_List[key]:
                with open(key, 'r') as tweet_file:
                    raw_batch = islice(tweet_file, None)
                    for line in raw_batch:
                        tweet_item = json.loads(line)
                        if tweet_item['id'] in Tweet_List_Relevant_Dict_List[key]['true']:  # Has a key term.
                            f.write(line)
                tweet_file.close()
            else:
                print(key) #These mostly seem to be out of date-range (deleted older tweets?), but have vaccine terms...
    f.close()

# I don't want all of these in RAM.
# Relevant_Tweets = list()
# with open('data/All_Keywords_Relevant_Tweets_from_Initial_Dataset.json', 'r') as f:
#     Relevant_Tweets[0] = json.loads(f.readline())
#     f.close()

# Pull the keyword relevant Tweet IDs from the broad set. (The VSN_Twitter Org set is pulled below.)
from Tweet_File_Analysis_Functions import ListAllTweetIDs
Relevant_Keyword_Tweet_IDs = ListAllTweetIDs('data/All_Keywords_Relevant_Tweets_from_Initial_Dataset.json')
len(Relevant_Keyword_Tweet_IDs)  # 42,073.

import dill

if not os.path.isfile('data/Relevant_Conversations_Forest.gpkl'):# Don't redo it
    # Forever to load, but can't serialize output, so... (Fixed with dill.)
    from Visualize import Get_Threads
    Thread_Forest, Thread_Sets = Get_Threads()
    # Forest is a list of Graphs, one per conversation.

    # We want a sublist of trees that are relevant based on keywords, then one that includes a tweet in our ID list.
    Relevant_Conversations_Forest = list()
    number_found = 0
    for Tree in Thread_Forest:
        Match = False
        for tweetID in Relevant_Keyword_Tweet_IDs:
            if not Match:
                if Tree.has_node(tweetID):
                    Relevant_Conversations_Forest.append(Tree)
                    Match = True
                    number_found = number_found + 1
                    if number_found % 50 == 49:
                        print(number_found, " so far")

    len(Relevant_Conversations_Forest)  # This finds 2427 conversations. # Takes 4-5 hours. ARGH,

    with open('data/Relevant_Conversations_Forest.gpkl', 'wb') as outfile:
        dill.dump((Relevant_Conversations_Forest), outfile)
        outfile.close()

    with open('data/Conversations_Forest.gpkl', 'wb') as outfile:
        dill.dump((Thread_Forest), outfile)
        outfile.close()

#    with open('data/Conversations_Sets.gpkl', 'wb') as outfile:
#        dill.dump((Thread_Sets), outfile)
#        outfile.close()
#    Can't pickle generators


with open('data/Relevant_Conversations_Forest.gpkl', 'rb') as infile:
    Relevant_Conversations_Forest = dill.load(infile)
    infile.close()

with open('data/Conversations_Forest.gpkl', 'rb') as infile:
    Thread_Forest = dill.load(infile)
    infile.close()

# Can't pickle generators
# with open('data/Conversations_Sets.gpkl', 'rb') as infile:
#     Thread_Sets = dill.load(infile)
#     infile.close()
# Don't need this, and can recreate if needed

# To Do: Count total Tweets.
Total_Tweets = 0
for Tree in Relevant_Conversations_Forest:
    Total_Tweets = Total_Tweets + len(Relevant_Conversations_Forest)


# From thread structures (which include user IDS,) find tweets by WHO_VSN, and look at those threads.

VSN_IDs = [Member['id'] for Member in VSN_Peeps] # 54 Users.

TWStruct_VSN_Tweets_Only = [item for item in TWStruct if item[2] in VSN_IDs or item[3] in VSN_IDs] # 3685 Tweets.
TWStruct_VSN__Single_Tweet = [tweet[0] for tweet in TWStruct_VSN_Tweets_Only]
len(TWStruct_VSN__Single_Tweet)
# Now, find the trees in the graph forest that include those tweets.

# from Visualize import Get_Threads # Now pulled above for keyword relevant tweets. (Takes forever.)
# Thread_Forest, Thread_Sets = Get_Threads()
# Forest is a list of Graphs, one per conversation. We want a list of trees that have a user in VSN.

VSN_Conversations_Forest = list()

number_found = 0

# Takes from 12:30 - ~12:35 That's much faster.
# (That list is 42k tweets to check for, this is only 3,685. So easily 10x as many: time complexity at least nlogn)
if not os.path.isfile('data/VSN_Conversations_Forest.gpkl'):# Don't redo it
    for Tree in Thread_Forest:
        Match = False
        for tweetID in TWStruct_VSN__Single_Tweet:
            if not Match:
                if Tree.has_node(tweetID):
                    VSN_Conversations_Forest.append(Tree)
                    Match = True
                    number_found = number_found + 1
                    if number_found % 50 == 49:
                        print(number_found, " so far")

    with open('data/VSN_Conversations_Forest.gpkl', 'wb') as outfile:
        dill.dump((VSN_Conversations_Forest), outfile)
        outfile.close()

with open('data/VSN_Conversations_Forest.gpkl', 'rb') as infile:
    VSN_Conversations_Forest = dill.load(infile)
    infile.close()

len(VSN_Conversations_Forest) # Without "Match", this found 3685, including duplicates. Now, it's 1826 conversations.

# I'm getting too many unknowns. I need to list the ones I actually don't have and check / retrieve them:
AllUsers = []
for tree in VSN_Conversations_Forest:
    for node in tree.nodes:
        AllUsers.append(tree.nodes[node]['user'])
for tree in Relevant_Conversations_Forest:
    for node in tree.nodes:
        AllUsers.append(tree.nodes[node]['user'])
# 30k, with duplicates.
AllUserSet = set(AllUsers)
# 6093, deduplicated.
unknowns=list()
for u in AllUserSet:
    if str(u) not in Users_Classified.keys():
        unknowns.append(u)
# Lots of Suspended Users! (Ah. Likely Bots.)
MoreUsers = dict()
for i in unknowns:
    try:
        u = api.GetUser(i)
        MoreUsers[u.id] = u
    except Exception as e:
        MoreUsers[i] = repr(e) #Suspended or Deleted Accounts

# Add these too the user set.
Added= []
for u in MoreUsers:
    if type(u)==type({}):
        print(u)
        Users_Classified[u.id]=dict()
        Out = Classify_UserItem(u, User_Classes)
        Users_Classified[u.id] = Out
        Added.append(Out)




Susp_Msg = "TwitterError([{'code': 63, 'message': 'User has been suspended.'}])"
Suspended = [i for i in MoreUsers.keys() if type(MoreUsers[i])==type("a") and MoreUsers[i]==Susp_Msg]
Dead_Accounts = [i for i in MoreUsers.keys() if type(MoreUsers[i])==type("a") and not MoreUsers[i]==Susp_Msg]
from Tweet_File_Analysis_Functions import WriteNewList
WriteNewList(Suspended, 'data\suspended_users.json')
WriteNewList(Dead_Accounts, 'data\dead_accounts.json')


with open('data\suspended_users.json','r') as f:
    Suspended = json.loads(f.readline())
    f.close()
with open('data\dead_accounts.json','r') as f:
    Dead_Accounts = json.loads(f.readline())
    f.close()


# Add users detected as bots:
Bots = [u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.43]
# Sensitivity:
len([u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.35])
len([u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.41])
len([u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.43])
len([u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.45])
len([u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.5])


# from copy import deepcopy
Filtered_Relevant_Conversations_Forest = list()
for i in range(0,len(Relevant_Conversations_Forest)):
    OK = True
    for node in Relevant_Conversations_Forest[i].nodes:
        if Relevant_Conversations_Forest[i].nodes[node]['user'] in Suspended:
            OK = False # 96 Accounts
        if Relevant_Conversations_Forest[i].nodes[node]['user'] in Bots:
            OK = False # None
        if Relevant_Conversations_Forest[i].nodes[node]['user'] in Dead_Accounts:
            OK = False
    if OK:
        Filtered_Relevant_Conversations_Forest.append(Relevant_Conversations_Forest[i])

Filtered_VSN_Conversations_Forest = list()
for i in range(0,len(VSN_Conversations_Forest)):
    OK = True
    for node in VSN_Conversations_Forest[i].nodes:
        if VSN_Conversations_Forest[i].nodes[node]['user'] in Suspended:
            OK = False # 12 such accounts
        if VSN_Conversations_Forest[i].nodes[node]['user'] in Bots:
            OK = False #None
        if VSN_Conversations_Forest[i].nodes[node]['user'] in Dead_Accounts:
            OK = False
    if OK:
        Filtered_VSN_Conversations_Forest.append(VSN_Conversations_Forest[i])

BotUsers = dict()
for i in Bots:
    try:
        u = api.GetUser(i)
        BotUsers[u.id] = u
    except:
        BotUsers[i] = "Suspended"
    # ALL are now suspended...

MaybeBots = [u for u in Users_Classified if 'BotOMeter' in Users_Classified[u].keys() and Users_Classified[u]['BotOMeter']>.25]
MaybeBotUsers = dict()
for i in MaybeBots:
    try:
        u = api.GetUser(i)
        MaybeBotUsers[u.id] = u
    except:
        MaybeBotUsers[i] = "Suspended"
    # ALL are now suspended...










def Tsizes(Thread_Forest):
    TSizes = dict()
    TSizes['l'] = []
    for Tree in Thread_Forest:
        size = len(Tree)
        if size in TSizes.keys():
            TSizes[size] = TSizes[size] + 1
        else:
            TSizes[size] = 1
        TSizes['l'].append(size)
    TSizes['v'] = []  # in same order as traversing keys
    TSizes['k'] = []  # also needed to preserve order
    for key in TSizes.keys():
        TSizes['k'].append(key)
        TSizes['v'].append(TSizes[key])
    return(TSizes)

# Only has 2+ tweet conversations. Where are the singletons?
# They aren't threads - all these are threads, by construction.

VSN_CSizes = Tsizes(VSN_Conversations_Forest)
Relevant_CSizes = Tsizes(Relevant_Conversations_Forest)

from Visualize import Thread_Types, Thread_Metrics
VSN_Metrics = Thread_Metrics(False, False, VSN_Conversations_Forest)
Relevant_Metrics = Thread_Metrics(False, False, Relevant_Conversations_Forest)

VSN_Types = Thread_Types(VSN_Conversations_Forest, Users_Classified)
Relevant_Types = Thread_Types(Relevant_Conversations_Forest, Users_Classified)




import matplotlib.pyplot as plt
import numpy

plt.hist(VSN_CSizes['l'])
width = 1.0
plt.bar(VSN_CSizes.keys(), VSN_CSizes.values(), width, color='g')
plt.bar(Relevant_CSizes.keys(), Relevant_CSizes.values(), width, color='r')

both=[]
both.extend(VSN_CSizes['l'])
both.extend(Relevant_CSizes['l'])
bins = numpy.linspace(0, 15, 100)

plt.hist(VSN_CSizes['l'], range=(2,20), bins=19, alpha=0.5, density=1, label='VSN')
plt.hist(Relevant_CSizes['l'], range=(2,20), bins=19, alpha=0.5, density=1, label='Relevant')
plt.legend(loc='upper right')
plt.show()
# Or:
both=[[],[]]
both[0] = VSN_CSizes['l']
both[1] = Relevant_CSizes['l']
plt.hist(both, 100, range=(1,20), histtype='bar', density=True, stacked=True)

from scipy import stats
print(stats.ttest_ind(VSN_CSizes['l'],Relevant_CSizes['l']))



# Need to check overlap between the sets. (Easy way is to check how many VSN_Conversations are in the Relevant set.)
Both_Forest = list()
for Tree in Relevant_Conversations_Forest:
    Match = False
    for tweetID in TWStruct_VSN__Single_Tweet:
        if not Match:
            if Tree.has_node(tweetID):
                Both_Forest.append(Tree)
                Match = True
                number_found = number_found + 1
                if number_found % 50 == 49:
                    print(number_found, " so far")
len(Both_Forest) # 255
Both_Tweet_Count = 0
for tree in Both_Forest:
    for item in tree:
        Both_Tweet_Count = Both_Tweet_Count + 1
# 1257

# Done getting data

###########################################################
#### Functions to analyze the Conversation Structures  ####
###########################################################

# Note: (Also relevant for the above) - can't pickle or json-ify the networkx graph. Need to re-run the script instead :(
# Json writes something, but fails - see below.
# from Tweet_File_Analysis_Functions import WriteNewList
# WriteNewList(VSN_Conversations_Forest, 'data/VSN_Conversations_Forest.json')

# 1. Given how I defined Monologue, Reply, etc. I need to check which are which.
len(nx.nodes(VSN_Conversations_Forest[17]))

import networkx as nx
def Recurse_Pred(Digraph, Node):
    Curr_List=list()
    preds = nx.DiGraph.predecessors(Digraph, Node)
    for each_pred in preds:
        Curr_List.append(each_pred)
        Curr_List.extend(Recurse_Pred(Digraph, each_pred))
    return(Curr_List)

def RST_Classify_Tree(Digraph_Input):
    # If a path exists where user A has a node with ancestor user B, which itself has and ancestor by A, A conversed.
    # Anything with an out-degree of 0 is a leaf. I can grab the predecessors and check...
    nodelist = list(Digraph_Input.nodes)
    if len(Digraph_Input) == 2:
        if Digraph_Input.nodes(nodelist[0])==Digraph_Input.nodes(nodelist[1]):
            return("Reply")
        else:
            return("Monologue")
    users = set()
    for node in Digraph_Input:
        users.add(Digraph_Input.nodes[node]['user'])
    if len(users)==1:
        return ("Monologue")
    # build lists:
    conversors = set()
    predlist= dict()
    userpredlist = dict()
    for node in nodelist:
        predlist[node] = Recurse_Pred(Digraph_Input, node)
        userpredlist[node] = set()
        for n in predlist[node]:
            userpredlist[node].add(Digraph_Input.nodes[n]['user'])
    for node in nodelist:
        this_user = Digraph_Input.nodes[node]['user']
        for pred in predlist[node]:
            if Digraph_Input.nodes[pred]['user'] != this_user:
                if this_user in userpredlist[pred]:
                    conversors.add(this_user)
                    conversors.add(Digraph_Input.nodes[pred]['user'])
    if len(conversors) > 2:
        return("Multilogue")
    elif len(conversors) > 1:
        return("Dialogue")
    else:
        return("Reply")

################################################################
#### Now, we actually Analyze the Conversation Structures!  ####
################################################################

Relevant_Conv_Classified_Dict = dict()

for i in Relevant_Conversations_Forest:
    answer = RST_Classify_Tree(i)
    if answer in Relevant_Conv_Classified_Dict.keys():
        Relevant_Conv_Classified_Dict[answer] = Relevant_Conv_Classified_Dict[answer] + 1
    else:
        Relevant_Conv_Classified_Dict[answer] = 1
# {'Multilogue': 487, 'Dialogue': 546, 'Reply': 1308, 'Monologue': 86}

Relevant_Conv_Classified_Nested_Dict = dict()

for tree in Relevant_Conversations_Forest:
    userclasslist = Users_Classlist(tree)
    answer = RST_Classify_Tree(tree)
    if answer in Relevant_Conv_Classified_Nested_Dict.keys():
        Relevant_Conv_Classified_Nested_Dict[answer]['count'] = Relevant_Conv_Classified_Nested_Dict[answer]['count']+ 1
        if userclasslist in Relevant_Conv_Classified_Nested_Dict[answer]:
            Relevant_Conv_Classified_Nested_Dict[answer][userclasslist] = \
                Relevant_Conv_Classified_Nested_Dict[answer][userclasslist] + 1
        else: Relevant_Conv_Classified_Nested_Dict[answer][userclasslist] = 1
    else:
        Relevant_Conv_Classified_Nested_Dict[answer] = dict()
        Relevant_Conv_Classified_Nested_Dict[answer]['count'] = 1
        Relevant_Conv_Classified_Nested_Dict[answer][userclasslist] = 1
# {'Multilogue': {'count': 487, "['Company', 'Unknown']": 174, "['Academic', 'Organization', 'Unknown']": 3, "['Company', 'Organization', 'Unknown']": 52, "['Company', 'Personal', 'Unknown']": 42, "['Company', 'Organization', 'Personal', 'Unknown']": 16, "['Unknown']": 90, "['Personal', 'Unknown']": 28, "['Academic', 'Unknown']": 10, "['Academic', 'Company', 'Unknown']": 22, "['Academic', 'Company', 'Organization']": 1, "['Organization', 'Unknown']": 14, "['Academic', 'Company', 'Organization', 'Unknown']": 9, "['Academic', 'Personal', 'Unknown']": 3, "['Government', 'Unknown']": 2, "['Organization', 'Personal', 'Unknown']": 4, "['Government', 'Organization', 'Unknown']": 1, "['Company', 'Government', 'Organization', 'Personal', 'Unknown']": 4, "['Academic', 'Company', 'Personal', 'Unknown']": 7, "['Company', 'Government', 'Unknown']": 3, "['Company', 'Government', 'Personal', 'Unknown']": 1, "['Company', 'Personal']": 1}, 'Dialogue': {'count': 546, "['Company', 'Unknown']": 157, "['Company', 'Organization']": 13, "['Company', 'Personal']": 6, "['Personal', 'Unknown']": 44, "['Unknown']": 193, "['Government', 'Unknown']": 19, "['Organization', 'Unknown']": 33, "['Academic', 'Company', 'Unknown']": 4, "['Academic', 'Unknown']": 13, "['Company', 'Personal', 'Unknown']": 17, "['Academic']": 1, "['Company', 'Organization', 'Unknown']": 14, "['Academic', 'Personal', 'Unknown']": 1, "['Company']": 13, "['Academic', 'Organization', 'Personal', 'Unknown']": 1, "['Academic', 'Government', 'Organization']": 1, "['Organization', 'Personal']": 2, "['Company', 'Organization', 'Personal', 'Unknown']": 2, "['Organization', 'Personal', 'Unknown']": 6, "['Academic', 'Company']": 3, "['Government', 'Personal', 'Unknown']": 1, "['Government', 'Organization', 'Unknown']": 1, "['Company', 'Government', 'Unknown']": 1}, 'Reply': {'count': 1308, "['Unknown']": 473, "['Company', 'Unknown']": 285, "['Organization']": 36, "['Personal', 'Unknown']": 81, "['Organization', 'Personal']": 7, "['Company', 'Organization']": 39, "['Academic']": 4, "['Government', 'Unknown']": 25, "['Organization', 'Unknown']": 121, "['Academic', 'Unknown']": 19, "['Government', 'Organization']": 8, "['Company']": 80, "['Academic', 'Company', 'Unknown']": 9, "['Company', 'Personal']": 24, "['Company', 'Organization', 'Unknown']": 22, "['Academic', 'Organization', 'Unknown']": 1, "['Organization', 'Personal', 'Unknown']": 8, "['Academic', 'Company']": 8, "['Personal']": 5, "['Company', 'Government', 'Unknown']": 4, "['Company', 'Government']": 4, "['Academic', 'Organization']": 7, "['Academic', 'Company', 'Organization']": 1, "['Government', 'Personal']": 3, "['Company', 'Personal', 'Unknown']": 25, "['Academic', 'Organization', 'Personal']": 2, "['Academic', 'Government']": 1, "['Company', 'Organization', 'Personal', 'Unknown']": 1, "['Academic', 'Company', 'Organization', 'Unknown']": 1, "['Academic', 'Personal', 'Unknown']": 1, "['Government', 'Organization', 'Unknown']": 1, "['Academic', 'Company', 'Personal', 'Unknown']": 1, "['Government']": 1}, 'Monologue': {'count': 86, "['Organization']": 23, "['Unknown']": 33, "['Academic']": 6, "['Government']": 7, "['Company']": 15, "['Personal']": 2}}


VSN_Conv_Classified_Dict = dict()

for i in VSN_Conversations_Forest:
    answer = RST_Classify_Tree(i)
    if answer in VSN_Conv_Classified_Dict.keys():
        VSN_Conv_Classified_Dict[answer] = VSN_Conv_Classified_Dict[answer] + 1
    else:
        VSN_Conv_Classified_Dict[answer] = 1
# {'Multilogue': 108, 'Reply': 1197, 'Dialogue': 442, 'Monologue': 79}


VSN_Conv_Classified_Nested_Dict = dict()

for tree in VSN_Conversations_Forest:
    userclasslist = Users_Classlist(tree)
    answer = RST_Classify_Tree(tree)
    if answer in VSN_Conv_Classified_Nested_Dict.keys():
        VSN_Conv_Classified_Nested_Dict[answer]['count'] = VSN_Conv_Classified_Nested_Dict[answer]['count']+ 1
        if userclasslist in VSN_Conv_Classified_Nested_Dict[answer]:
            VSN_Conv_Classified_Nested_Dict[answer][userclasslist] = \
                VSN_Conv_Classified_Nested_Dict[answer][userclasslist] + 1
        else: VSN_Conv_Classified_Nested_Dict[answer][userclasslist] = 1
    else:
        VSN_Conv_Classified_Nested_Dict[answer] = dict()
        VSN_Conv_Classified_Nested_Dict[answer]['count'] = 1
        VSN_Conv_Classified_Nested_Dict[answer][userclasslist] = 1
# {'Multilogue': {'count': 108, "['Company', 'Organization', 'Unknown']": 8, "['Organization', 'Unknown']": 7, "['Unknown']": 51, "['Company', 'Unknown']": 24, "['Personal', 'Unknown']": 10, "['Company', 'Personal', 'Unknown']": 4, "['Government', 'Unknown']": 1, "['Company', 'Organization', 'Personal', 'Unknown']": 1, "['Organization', 'Personal', 'Unknown']": 1, "['Company', 'Government', 'Unknown']": 1}, 'Reply': {'count': 1197, "['Organization', 'Unknown']": 169, "['Organization']": 23, "['Company', 'Organization']": 52, "['Organization', 'Personal']": 12, "['Company']": 9, "['Company', 'Unknown']": 128, "['Unknown']": 644, "['Academic', 'Organization']": 11, "['Company', 'Organization', 'Unknown']": 14, "['Company', 'Organization', 'Personal']": 1, "['Academic', 'Unknown']": 7, "['Academic', 'Company']": 1, "['Academic', 'Company', 'Organization', 'Personal']": 1, "['Personal', 'Unknown']": 49, "['Government', 'Organization']": 7, "['Company', 'Personal', 'Unknown']": 5, "['Organization', 'Personal', 'Unknown']": 5, "['Government', 'Unknown']": 27, "['Company', 'Government', 'Organization', 'Unknown']": 1, "['Academic', 'Company', 'Organization']": 1, "['Company', 'Government']": 7, "['Company', 'Government', 'Unknown']": 3, "['Academic', 'Organization', 'Personal']": 1, "['Government']": 13, "['Government', 'Organization', 'Unknown']": 1, "['Government', 'Personal', 'Unknown']": 1, "['Company', 'Organization', 'Personal', 'Unknown']": 1, "['Academic', 'Organization', 'Unknown']": 1, "['Academic', 'Government']": 2}, 'Dialogue': {'count': 442, "['Company', 'Organization']": 18, "['Organization']": 5, "['Organization', 'Unknown']": 49, "['Company', 'Unknown']": 70, "['Company', 'Government', 'Organization']": 1, "['Unknown']": 254, "['Company']": 3, "['Organization', 'Personal', 'Unknown']": 1, "['Company', 'Organization', 'Unknown']": 5, "['Organization', 'Personal']": 1, "['Academic', 'Company', 'Organization']": 2, "['Academic', 'Organization']": 1, "['Academic', 'Organization', 'Unknown']": 1, "['Personal', 'Unknown']": 10, "['Academic', 'Company']": 1, "['Academic', 'Unknown']": 3, "['Government', 'Unknown']": 8, "['Academic', 'Government', 'Organization']": 1, "['Company', 'Government']": 3, "['Government', 'Personal', 'Unknown']": 1, "['Company', 'Organization', 'Personal']": 1, "['Company', 'Personal', 'Unknown']": 1, "['Government', 'Organization']": 1, "['Academic', 'Company', 'Organization', 'Unknown']": 1}, 'Monologue': {'count': 79, "['Organization']": 6, "['Unknown']": 53, "['Government']": 20}}



# from Tweet_File_Analysis_Functions import Classify_User


#######################
#### Try a picture ####
#######################

Datasets = ['VSN Members','Relevant Conversations']
ConvTypes = ['Monologue','Reply','Dialogue','Multilogue']
UserTypes = ['Organization', 'Expert','Other', 'Etc']

Datasets_to_ConvTypes_values = [79, 1197, 442, 108,
                                86, 1308, 546, 487]
Dataset_to_ConvTypes_MapSource = [0, 0, 0, 0,
                                  1, 1, 1, 1]
Dataset_to_ConvTypes_MapDest = [2,3,4,5,
                                2,3,4,5]

ConvTypes_to_UserTypes_values = \ #Fake Data! Doubled entries to split per dataset.
    [34, 23, 900, 300, 300,
     68, 40, 405, 243, 184,
     1,1,1,1,1,
     1,1,1,1,1,
     0,0,0,0,0,
     0,0,0,0,0,
     1,1,1,1,1,
     0,0,0,0,0]

ConvTypes_to_UserTypes_MapSource =

ConvTypes_to_UserTypes_MapDest =

# from Visualize import Sankey_Diagram
#
# Visual = Sankey_Diagram(['VSN Members','Relevant Conversations','Monologue','Reply','Dialogue','Multilogue'], [0, 0, 0, 0, 1, 1, 1, 1], [2,3,4,5,2,3,4,5], [79, 1197, 442, 108, 86, 1308, 546, 487])

# Sankey diagram hould be expanded to a third column with who was involved in the conversations

# Fake Data:
PPLType = ['Organization', 'Expert','Other', 'Etc']
From = [2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5]
To = [6,6,6,6,6,6,6,6,7,7,7,7,7,7,7,7,8,8,8,8,8,8,8,8,9,9,9,9,9,9,9,9]
Values = [34, 23, 900, 300, 300,
          68, 40, 405, 243, 184,
          1,1,1,1,1,
          1,1,1,1,1,
          0,0,0,0,
          0,0,0,0,
          1,1,1,1,
          0,0,0,0]

This works, but the numbers are wrongly set up. Hmmm.
Sankey_Diagram(['VSN Members','Relevant Conversations',
                     'Monologue','Reply','Dialogue','Multilogue',
                     'Organization', 'Expert','Other'],
                    [0, 0, 0, 0, 1, 1, 1, 1,
                     2,2,2,3,3,3,4,4,4,5,5,5,2,2,2,3,3,3,4,4,4,5,5,5],
                    [2,3,4,5,2,3,4,5,
                     6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8],
                    [79, 1197, 442, 108, 86, 1308, 546, 487,
                     50,20,4,800,200,197,300,120,22,60,30,18,40,30,16,1000,200,108,200,300,46,200,220,67],
                    [0, 0, 0, 0, 1, 1, 1, 1, 0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1])

# 79, 1197, 442, 108, \
# 86, 1308, 546, 487,
# 170, 2600, 1000, 590

# 34, 23, 900, 300, 300, 68, 40, 405, 243, 184, 1,1,1,1,1, 1,1,1,1,1, 0,0,0,0, 1,1,1,1],

Relevant_Conv_Userlist = list()
for tree in Relevant_Conversations_Forest:
    for node in tree:
        Relevant_Conv_Userlist.append(tree.nodes[node]['user'])
Relevant_Conv_Userset = set(Relevant_Conv_Userlist)
len(set(Relevant_Conv_Userlist))  # 4,417

Relevant_Conv_Tweet_Count = 0
for tree in Relevant_Conversations_Forest:
    for item in tree:
        Relevant_Conv_Tweet_Count = Relevant_Conv_Tweet_Count + 1
# 24,192



VSN_Conv_Userlist = list()
for tree in VSN_Conversations_Forest:
    for node in tree:
        VSN_Conv_Userlist.append(tree.nodes[node]['user'])
#2,208

for tree in VSN_Conversations_Forest:
    for node in tree:
        VSN_Conv_Userlist.append(tree.nodes[node]['user'])
VSN_Conv_Userset = set(VSN_Conv_Userlist)
len(set(VSN_Conv_Userlist)) # 2,208

VSN_Conv_Tweet_Count = 0
for tree in VSN_Conversations_Forest:
    for item in tree:
        VSN_Conv_Tweet_Count = VSN_Conv_Tweet_Count + 1
print(VSN_Conv_Tweet_Count)


# Now, we extract the user types in each conversation.


Relevant_Conversation_User_Summaries = dict()
Relevant_Conversation_User_Summaries['VSN'] = 0
Relevant_Conversation_User_Summaries['Expert'] = 0
Relevant_Conversation_User_Summaries['Organization'] = 0
Relevant_Conversation_User_Summaries['None'] = 0
Relevant_Conversation_User_Summaries['BotScore'] = list()
Relevant_Conversation_User_Summaries['Class'] = dict()


for user in Relevant_Conv_Userset:
    if str(user) in Users_Classified:
        Relevant_Conversation_User_Summaries['VSN'] = Relevant_Conversation_User_Summaries['VSN'] + Users_Classified[str(user)]['VSN']
        Relevant_Conversation_User_Summaries['Expert'] = Relevant_Conversation_User_Summaries['Expert'] + Users_Classified[str(user)]['Expert']
        Relevant_Conversation_User_Summaries['Organization'] = Relevant_Conversation_User_Summaries['Organization'] + Users_Classified[str(user)]['Organization']
        Relevant_Conversation_User_Summaries['None'] = \
            Relevant_Conversation_User_Summaries['None'] \
            + int(not (Users_Classified[str(user)]['VSN'] or Users_Classified[str(user)]['Expert'] or Users_Classified[str(user)]['Organization']))
        if 'BotOMeter' in Users_Classified[str(user)]:
            Relevant_Conversation_User_Summaries['BotScore'].append(Users_Classified[str(user)]['BotOMeter'])
        # if 'Wikidata_Class' in Users_Classified[str(user)]:
        #     if Users_Classified[str(user)]['Wikidata_Class'] in Relevant_Conversation_User_Summaries['Class']:
        #         Relevant_Conversation_User_Summaries['Class'][Users_Classified[str(user)]['Wikidata_Class']] = \
        #             Relevant_Conversation_User_Summaries['Class'][Users_Classified[[str(user)]['Wikidata_Class']]] + 1
        #     else:
        #         Relevant_Conversation_User_Summaries['Class'][[Users_Classified[str(user)]['Wikidata_Class']]]
    else:
        print(user)  # Many Missing. Argh!

len([s for s in Relevant_Conversation_User_Summaries['BotScore'] if s < 0])  # 182
len([s for s in Relevant_Conversation_User_Summaries['BotScore'] if s == 0]) # 0

from matplotlib import pyplot as plt
Scores = Relevant_Conversation_User_Summaries['BotScore']
Scores = [s for s in Scores if s >= 0]
plt.hist(Scores, 100)
len([s for s in Scores if s > 0.25])  # 21
len([s for s in Scores if s > 0.5])  # 10


VSN_Conversation_User_Summaries = dict()
VSN_Conversation_User_Summaries['VSN'] = 0
VSN_Conversation_User_Summaries['Expert'] = 0
VSN_Conversation_User_Summaries['Organization'] = 0
VSN_Conversation_User_Summaries['None'] = 0
VSN_Conversation_User_Summaries['BotScore'] = list()
VSN_Conversation_User_Summaries['Class'] = dict()

for user in VSN_Conv_Userset:
    if str(user) in Users_Classified:
        VSN_Conversation_User_Summaries['VSN'] = VSN_Conversation_User_Summaries['VSN'] + Users_Classified[str(user)]['VSN']
        VSN_Conversation_User_Summaries['Expert'] = VSN_Conversation_User_Summaries['Expert'] + Users_Classified[str(user)]['Expert']
        VSN_Conversation_User_Summaries['Organization'] = VSN_Conversation_User_Summaries['Organization'] + Users_Classified[str(user)]['Organization']
        VSN_Conversation_User_Summaries['None'] = \
            VSN_Conversation_User_Summaries['None'] \
            + int(not (Users_Classified[str(user)]['VSN'] or Users_Classified[str(user)]['Expert'] or Users_Classified[str(user)]['Organization']))
        if 'BotOMeter' in Users_Classified[str(user)]:
            VSN_Conversation_User_Summaries['BotScore'].append(Users_Classified[str(user)]['BotOMeter'])
        # if 'Wikidata_Class' in Users_Classified[str(user)]:
        #     if Users_Classified[str(user)]['Wikidata_Class'] in VSN_Conversation_User_Summaries['Class']:
        #         VSN_Conversation_User_Summaries['Class'][Users_Classified[str(user)]['Wikidata_Class']] = \
        #             VSN_Conversation_User_Summaries['Class'][Users_Classified[[str(user)]['Wikidata_Class']]] + 1
        #     else:
        #         VSN_Conversation_User_Summaries['Class'][[Users_Classified[str(user)]['Wikidata_Class']]]
    else:
        print(user)


for u in list(Users_Classified.keys())[1:100]:
    if Users_Classified[u]["verified"]:
        print(Users_Classified[u].keys())
# Can I collapse nodes that are by the same user, then check alternation? That doesn't work.
# (A, C by 1, B, D by 2, edges AB, AC, CD, BD, can't collapse without creating incorrect edge.)
# Note: this is done above by RST_Classify_Tree()




# 2. Find tweets mentioning keywords, and look at conversations with those keywords anywhere in-thread.
# Done Above!

# First, I want to compile all the conversation data into a new file.
# This means finding all the users in the conversations, and scanning the relevant files.
#
# # First get userlist and the tweets per user:
# Tweet_By_User = dict()
# for Tree in VSN_Conversations_Forest:
#     for node in Tree.nodes:
#         user = Tree.node[node]['user']
#         if user not in Tweet_By_User.keys():
#             Tweet_By_User[user] = [node] # List with one item.
#         else:
#             Tweet_By_User[user].append(node)
#
# len(Tweet_By_User.keys()) # 2208 Users
#
#
# if os.path.isfile('Convo_Tweets_In_Tweet_By_ID_Files_List.json'):
#     Tweets_In_Tweet_By_ID_Files_List = GetListFile('Convo_Tweets_In_Tweet_By_ID_Files_List.json')
# else:
#     Tweets_In_Tweet_By_ID_Files_List = list()
#
# from Tweet_File_Analysis_Functions import GetListFile, WriteNewList, Get_FileList_Of_JSON_Files
# if os.path.isfile('Convo_Pulled_Userlist_Updating.json'):
#     Pulled = GetListFile('Convo_Pulled_Userlist_Updating.json')
# else:
#     Pulled = list()
# # Use the dict to scan user files:
# for user in list(Tweet_By_User.keys()):
#     if user not in Pulled:
#         # Find the file:
#         files = Get_FileList_Of_JSON_Files("data", prefix="Tweets_by_"+ str(user) + "_back")
#         Pulled.append(user)
#         WriteNewList(Pulled, 'Convo_Pulled_Userlist_Updating.json')
#     if len(files)>0:
#         # scan the file and add relevant tweets to compilation file.
#         with open(files[0]) as f:
#             for line in f:
#                 tweet = json.loads(line)
#                 if tweet['id'] in Tweet_By_User[user]:
#                     with open("data/VSN_Conversation_Tweets.json", 'a') as o:
#                         o.write(line)
#                         # o.write('\n') # Writing line that already has \n.
#                         o.close()
#             f.close()
#
#         # print(files)
#         # print(Tweet_By_User[user])
#     else:
#         Tweets_In_Tweet_By_ID_Files_List.append(Tweet_By_User[user])
#         WriteNewList(Tweets_In_Tweet_By_ID_Files_List, 'Convo_Tweets_In_Tweet_By_ID_Files_List.json')
#         # Later, I need to scan all the Tweets_By_ID files.
#         # It's later.
#     # Whoops. That isn't flat.
#     Tweets_In_Tweet_By_ID_Files_List = [item for sublist in Tweets_In_Tweet_By_ID_Files_List for item in sublist]
#
# By_ID_files = Get_FileList_Of_JSON_Files("data", prefix="tweets_By_ID_at") # 363 files.
#
# with open("data/VSN_Conversation_Tweets.json", 'a') as o:
#     for file in By_ID_files:
#         with open(file) as f:
#             for line in f:
#                 tweet = json.loads(line)
#                 if tweet['id'] in Tweets_In_Tweet_By_ID_Files_List:
#                     o.write(line)
#                     # o.write('\n') # Writing line that already has \n.
#         f.close()
#     o.close()
#     #print(VSN_Conversations_Forest[00000][node].keys())#['user'])

# Now, I can look at them...















# Later - Find tweets in the 10K dataset, and look at those threads, if any.

def get_tweetlist_from_tabbed_file(filename):
    import csv
    ID_List = []
    with open(filename, newline='') as Tweets_plus_csv:
        reader = csv.reader(Tweets_plus_csv, delimiter='\t')
        next(reader, None)
        for tweet in reader:
            ID_List.append(tweet[0])
    return(ID_List)

Tweetlist = get_tweetlist_from_tabbed_file("2018_ajph_weaponized_health_10k_data.txt")

AJPH_10K_Conversations_Forest = list()
number_found = 0
for Tree in Thread_Forest:
    Match = False
    for tweetID in Tweetlist:
        if not Match:
            if Tree.has_node(tweetID):
                AJPH_10K_Conversations_Forest.append(Tree)
                Match = True
                number_found = number_found + 1
                if number_found % 50 == 49:
                    print(number_found, " so far")
