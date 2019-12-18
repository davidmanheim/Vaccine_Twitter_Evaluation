import json
import os, time
import networkx as nx

# Get the data on users, on thread structures, and then scan the full dataset for what fits where, etc.
with open("data\Classified_Users_With_BotOrNot_One_line.json", 'r') as r:
    Users_Classified = json.loads(r.readline())
    r.close()

with open("data\Thread_Tweet_Structure_at_1563435934.7016308.json", 'r') as r:
    TWStruct = json.loads(r.readline())
    r.close()

with open("data\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json",'r') as r:
    VSN_Peeps = json.loads(r.readline())
    r.close()

VSN_IDs = [Member['id'] for Member in VSN_Peeps] # 54 Users.

# Need to Scan all files for tweets mentioning vaccine keywords.
# The relevant fileset is:
from Tweet_File_Analysis_Functions import Scan_Files_With_Function_Filter, Get_FileList_Of_JSON_Files, RelevantTweet,\
    ListAllTweetIDs, TweetByUser, Scan_Files_For_Thread_Items
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


if not os.path.isfile('data\TweetSet_All_VSN_Tweets.json'):
    Tweet_List_VSN_All = \
        Scan_Files_With_Function_Filter(Filelist=All_Tweet_Files, Filter=TweetByUser, AggNotList=False, Silent=True,
                                        Userlist=VSN_IDs, DateRange=DateRange)

    Tweet_ID_List = []
    for userfile in Tweet_List_VSN_All.keys():
        if (True in Tweet_List_VSN_All[userfile].keys()):
            Tweet_ID_List.extend(Tweet_List_VSN_All[userfile][True])
    # Total: 35,587

    Scan_Files_For_Thread_Items(Tweet_ID_List, All_Tweet_Files, 'data\TweetSet_All_VSN_Tweets.json', False)

# Need to load all tweets by line, also, too much data.
#with open('data\TweetSet_All_VSN_Tweets.json','r') as f:
#    VSN_AllTweets=json.loads(f.readline())
#    f.close()

len([tweet for user in Tweet_List_VSN_All for tweet in user]) # 41,120
len([tweet for user in Tweet_List_VSN_All for tweet in user if tweet[]]) # 41,120


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


# with open('data/Relevant_Conversations_Forest.gpkl', 'rb') as infile:
#     Relevant_Conversations_Forest = dill.load(infile)
#     infile.close()

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

# if any are unclassified / not in users_classified, add them: (rerun other scripts afterwards.)

for user in MoreUsers:
    if not type(MoreUsers[user]) == type("string"):
        Classified_Data = Classify_UserItem(MoreUsers[user]._json, User_Classes)
        Users_Classified[str(MoreUsers[user].id)] = dict()
        for key in Classified_Data[user].keys():
            Users_Classified[str(MoreUsers[user].id)][key] = Classified_Data[user][key]

for user in MoreUsers:
    if not type(MoreUsers[user]) == type("string"):
        if 'Website' in Users_Classified[str(MoreUsers[user].id)]:
            URL = Users_Classified[str(MoreUsers[user].id)]['Website']
            check = Check_Wikidata(MoreUsers[user]._json['entities']['url']['urls'][0]['expanded_url'])
            if check == 1:
                print ("we have Wiki for " + URL)
                Users_Classified[str(MoreUsers[user].id)]["Wikidata"] = Pull_Wikidata_Type(URL)

To_get = [str(key) for key in MoreUsers if not type(MoreUsers[key]) == type("string") and 'BotOMeter' not in Users_Classified[str(key)].keys()]
# Now I run the BotOrNot script in User_Extraction.

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

# Check if these accounts have been suspended.
CheckBotUsers = dict()
for i in Bots:
    try:
        u = api.GetUser(i)
        CheckBotUsers[u.id] = u
    except Exception as e:
        CheckBotUsers[i] = repr(e) #Suspended or Deleted Accounts

Suspended_Count = 0
Bots_Count = 0
Dead_Count = 0
# from copy import deepcopy
Filtered_Relevant_Conversations_Forest = list()
for i in range(0,len(Relevant_Conversations_Forest)):
    OK = True
    for node in Relevant_Conversations_Forest[i].nodes:
        if Relevant_Conversations_Forest[i].nodes[node]['user'] in Suspended:
            OK = False # 93 Accounts
            Suspended_Count = Suspended_Count +1
        if Relevant_Conversations_Forest[i].nodes[node]['user'] in Bots:
            OK = False # None
            Bots_Count = Bots_Count + 1
        if Relevant_Conversations_Forest[i].nodes[node]['user'] in Dead_Accounts:
            OK = False
            Dead_Count = Dead_Count + 1 # 3
    if OK:
        Filtered_Relevant_Conversations_Forest.append(Relevant_Conversations_Forest[i])


Suspended_Count = 0
Bots_Count = 0
Dead_Count = 0
Filtered_VSN_Conversations_Forest = list()
for i in range(0,len(VSN_Conversations_Forest)):
    OK = True
    for node in VSN_Conversations_Forest[i].nodes:
        if VSN_Conversations_Forest[i].nodes[node]['user'] in Suspended:
            OK = False # 12 such accounts
            Suspended_Count = Suspended_Count +1
        if VSN_Conversations_Forest[i].nodes[node]['user'] in Bots:
            OK = False #None
            Bots_Count = Bots_Count + 1
        if VSN_Conversations_Forest[i].nodes[node]['user'] in Dead_Accounts:
            OK = False #None
            Dead_Count = Dead_Count + 1
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


if not os.path.isfile('data/Filtered_VSN_Conversations_Forest.gpkl'):# Don't redo it

    with open('data/Filtered_VSN_Conversations_Forest.gpkl', 'wb') as outfile:
        dill.dump((Filtered_VSN_Conversations_Forest), outfile)
        outfile.close()

with open('data/Filtered_VSN_Conversations_Forest.gpkl', 'rb') as infile:
    VSN_Conversations_Forest = dill.load(infile)
    infile.close()

if not os.path.isfile('data/Filtered_Relevant_Conversations_Forest.gpkl'):# Don't redo it

    with open('data/Filtered_Relevant_Conversations_Forest.gpkl', 'wb') as outfile:
        dill.dump((Filtered_Relevant_Conversations_Forest), outfile)
        outfile.close()

with open('data/Filtered_Relevant_Conversations_Forest.gpkl', 'rb') as infile:
    Relevant_Conversations_Forest = dill.load(infile)
    infile.close()

def AllUsers(Forest):
    AllUsers = []
    for tree in Forest:
        for node in tree.nodes:
            AllUsers.append(tree.nodes[node]['user'])
    AllUserSet = set(AllUsers)
    return(AllUserSet)

def AllTweets(Forest):
    AllTweets = []
    for tree in Forest:
        for node in tree.nodes:
            AllTweets.append(node)
    AllTweetsSet = set(AllTweets)
    return(AllTweetsSet)

len(VSN_Conversations_Forest)
len(AllUsers(VSN_Conversations_Forest))
len(AllUsers(Relevant_Conversations_Forest))

len(AllTweets(VSN_Conversations_Forest))
len(AllTweets(Relevant_Conversations_Forest))

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
# 37,587 Total VSN Tweets...
# Only 1814 Are Conversations.
# Are 35,773 Singletons? No, that's not right: Many threads have multiple VSN-Member-Tweets.
# The old extracted data said 111,288 times, but 98,611 Singletons. That's because it didn't date-filter.
# After Date-filter, we need to find how many VSN-Tweets are not singletons (Quote-tweets or replies).


Relevant_CSizes = Tsizes(Relevant_Conversations_Forest)

from Visualize import Thread_Types, Thread_Metrics
VSN_Metrics = Thread_Metrics(False, False, VSN_Conversations_Forest)
Relevant_Metrics = Thread_Metrics(False, False, Relevant_Conversations_Forest)

VSN_Types = Thread_Types(VSN_Conversations_Forest, Users_Classified)
Relevant_Types = Thread_Types(Relevant_Conversations_Forest, Users_Classified)

# Who is in the conversations?
# 2 Categories, for now: Unknown vs. Personal (not general public, since they have a web site,) Corporate, Org, etc.

import matplotlib.pyplot as plt
import numpy

plt.hist(VSN_CSizes['l'])
width = 1.0
plt.bar(VSN_CSizes.keys(), VSN_CSizes.values(), width, color='g')
plt.bar(Relevant_CSizes.keys(), Relevant_CSizes.values(), width, color='r')

both=[]
both.extend(VSN_CSizes['l'])
both.extend(Relevant_CSizes['l'])

plt.hist(VSN_CSizes['l'], range=(2,21), bins=20, alpha=0.5, density=1, label='VSN')
plt.hist(Relevant_CSizes['l'], range=(2,21), bins=20, alpha=0.5, density=1, label='Relevant')
plt.xlim([2,21])
plt.xticks([2.5,5.5,10.5,15.5,20.5],[2,5,10,15,20])
plt.legend(loc='upper right')
plt.show()

len([x for x in VSN_CSizes['l'] if x>20])
len([x for x in Relevant_CSizes['l'] if x>20])
# Graph a big one:
test = [x for x in Relevant_Conversations_Forest if len(x)>1400][0]
test = [x for x in Relevant_Conversations_Forest if len(x)>200][1]
from matplotlib import colors
int_cmap = colors.ListedColormap(['k','b','y','g','r'])
nx.draw(test, pos=nx.spectral_layout(test), node_size=50,
        node_color=[test._node[node]['user'] for node in test],cmap=int_cmap)

len(set([test._node[node]['user'] for node in test]))
set([test._node[node]['user'] for node in test])
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

from Visualize import Users_Classlist

Relevant_Conv_Classified_Dict = dict()

Relevant_Conv_Classification_List = list()
for i in Relevant_Conversations_Forest:
    answer = RST_Classify_Tree(i)
    Relevant_Conv_Classification_List.append(answer)
    if answer in Relevant_Conv_Classified_Dict.keys():
        Relevant_Conv_Classified_Dict[answer] = Relevant_Conv_Classified_Dict[answer] + 1
    else:
        Relevant_Conv_Classified_Dict[answer] = 1
# {'Multilogue': 487, 'Dialogue': 546, 'Reply': 1308, 'Monologue': 86}
# Now filtered: {'Multilogue': 446, 'Dialogue': 521, 'Reply': 1278, 'Monologue': 86}

Relevant_Conv_Classified_Nested_Dict = dict()

for i in range(0,len(Relevant_Conversations_Forest)):
    userclasslist = Users_Classlist(Relevant_Conversations_Forest[i], Users_Classified)
    answer = Relevant_Conv_Classification_List[i]
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

if not os.path.isfile('data/Relevant_Conversations_Classifications.gpkl'):# Don't redo it

    with open('data/Relevant_Conversations_Classifications.gpkl', 'wb') as outfile:
        dill.dump([Relevant_Conv_Classification_List, Relevant_Conv_Classified_Dict, Relevant_Conv_Classified_Nested_Dict], outfile)
        outfile.close()

with open('data/Relevant_Conversations_Classifications.gpkl', 'rb') as infile:
    Relevant_Conv_Classification_List, Relevant_Conv_Classified_Dict, Relevant_Conv_Classified_Nested_Dict = dill.load(infile)
    infile.close()



VSN_Conv_Classified_Dict = dict()
VSN_Conv_Classification_List = list()
for tree in VSN_Conversations_Forest:
    answer = RST_Classify_Tree(tree)
    VSN_Conv_Classification_List.append(answer)
    if answer in VSN_Conv_Classified_Dict.keys():
        VSN_Conv_Classified_Dict[answer] = VSN_Conv_Classified_Dict[answer] + 1
    else:
        VSN_Conv_Classified_Dict[answer] = 1
# {'Multilogue': 108, 'Reply': 1197, 'Dialogue': 442, 'Monologue': 79}
# Now Filtered: {'Multilogue': 106, 'Reply': 1188, 'Dialogue': 441, 'Monologue': 79}

VSN_Conv_Classified_Nested_Dict = dict()

for i in range(0,len(VSN_Conversations_Forest)): #Why is this so slow? (Using 1+gb ram. Whoops.)
    userclasslist = Users_Classlist(VSN_Conversations_Forest[i], Users_Classified)
    answer = VSN_Conv_Classification_List[i]
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


if not os.path.isfile('data/VSN_Conversations_Classifications.gpkl'):# Don't redo it

    with open('data/VSN_Conversations_Classifications.gpkl', 'wb') as outfile:
        dill.dump([VSN_Conv_Classification_List, VSN_Conv_Classified_Dict, VSN_Conv_Classified_Nested_Dict], outfile)
        outfile.close()

with open('data/VSN_Conversations_Classifications.gpkl', 'rb') as infile:
    VSN_Conv_Classification_List, VSN_Conv_Classified_Dict, VSN_Conv_Classified_Nested_Dict = dill.load(infile)
    infile.close()


len([u for u in [user for user in Users_Classified if "Heuristic Class" in Users_Classified[user].keys()]
     if type(Users_Classified[user]["Heuristic Class"])==type(True)])


# For the Sankey Diagram, I need lists of how many in each class are only Orgs+Experts, vs. include the public:
# The Nested Dict has this info for me...

List_Of_Non_Org_Classes = ['Unknown','None','Personal']

def Org_Split_Calc(Classified_Dict, ListofClasses): #List of classes is the list of classes that count as non-Org/Expert
    Org_Split_Dict = dict()
    for Conv_Type in Classified_Dict.keys():
        Org_Split_Dict[Conv_Type] = [0,0] # To start. [0] is including a non-org, [1] is orgs only
        for key in Classified_Dict[Conv_Type].keys():
            if key != 'count':
                Matching_Classes = [Match for Match in ListofClasses if Match in key]
                if len(Matching_Classes)>0:
                    Org_Split_Dict[Conv_Type][0] = Org_Split_Dict[Conv_Type][0] + Classified_Dict[Conv_Type][key]
                else:
                    Org_Split_Dict[Conv_Type][1] = Org_Split_Dict[Conv_Type][1] + Classified_Dict[Conv_Type][key]
    return Org_Split_Dict


# These numbers were too large. Logic fixed now.
VSN_Answer = Org_Split_Calc(VSN_Conv_Classified_Nested_Dict, List_Of_Non_Org_Classes)
sum([VSN_Conv_Classified_Nested_Dict[Sub]['count'] for Sub in VSN_Conv_Classified_Nested_Dict.keys()]) #1814
sum([sum(pair) for pair in list(VSN_Answer.values())]) #10,884.
# Now 3628. That's still double-counting... (I was adding the 'count' key. Right. Fixed now.)
Relevant_Answer = Org_Split_Calc(Relevant_Conv_Classified_Nested_Dict, List_Of_Non_Org_Classes)
sum([Relevant_Conv_Classified_Nested_Dict[Sub]['count'] for Sub in Relevant_Conv_Classified_Nested_Dict.keys()])

# Totals From Users_Classified:
# 'Heuristic Class': {'Unknown': 47970, 'VSN': 53, 'Personal': 2874, 'Organization': 4037,
# 'Company': 17071, 'Government': 520, 'Nonprofit': 109, 'Other Org': 170, 'Data Source': 3,
# 'Person': 530, 'Academic': 787, 'News': 557, 'Research Org': 61, 'Business': 169, 'University': 13}


def Org_MultiSplit_Calc(Classified_Dict, ListofListofClasses):
    #This list is a list of lists, containing ordered membership set lists.
    #The lists must be able to assume no overlap for the logic to work.
    #(so that key "d" matches the first instead)
    Org_Split_Dict = dict()
    for Conv_Type in Classified_Dict.keys():
        Org_Split_Dict[Conv_Type] = [0 for i in ListofListofClasses] # One per class
        Org_Split_Dict[Conv_Type].append(0) #Plus the remaining items.
        for key in Classified_Dict[Conv_Type].keys():
            if key != 'count':
                # I need to match per list
                Matching_Classes = [[Match for Match in ListofClasses if Match in key] for ListofClasses in ListofListofClasses]
                Appearing = [len(Matching_Classes[Class]) for Class in range(0, len(Matching_Classes))]
                First_Found = False
                for pos in range(0, len(Appearing)):
                    if not First_Found:
                        if Appearing[pos]>0:
                            First_Appearance=pos
                            First_Found=True
                if First_Found:
                    Org_Split_Dict[Conv_Type][First_Appearance] = Org_Split_Dict[Conv_Type][First_Appearance] + Classified_Dict[Conv_Type][key]
                else:
                    Org_Split_Dict[Conv_Type][-1] = Org_Split_Dict[Conv_Type][-1] + Classified_Dict[Conv_Type][key]
    return Org_Split_Dict

# 'Heuristic Class': {'Unknown': 47970, 'VSN': 53, 'Personal': 2874, 'Organization': 4037,
# 'Company': 17071, 'Government': 520, 'Nonprofit': 109, 'Other Org': 170, 'Data Source': 3,
# 'Person': 530, 'Academic': 787, 'News': 557, 'Research Org': 61, 'Business': 169, 'University': 13}

Multisplit_ListOfLists = [["Unknown", "None"], ["Company", "Business", 'Other Org', 'Organization',"Person"]]
# Remaining is only: ["News", 'Nonprofit','Data Source','Academic','University','Research Org','Government','VSN'] (Checked!)

VSN_Multisplit_Answer = Org_MultiSplit_Calc(VSN_Conv_Classified_Nested_Dict, Multisplit_ListOfLists)
Relevant_Multisplit_Answer = Org_MultiSplit_Calc(Relevant_Conv_Classified_Nested_Dict, Multisplit_ListOfLists)

# from Tweet_File_Analysis_Functions import Classify_User


#######################
#### Try a picture ####
#######################

Datasets = ['VSN Members','Relevant Conversations']
ConvTypes = list(VSN_Conv_Classified_Dict.keys())
UserTypes = ['Includes Individuals', 'Organizations and Experts Only']


Datasets_to_ConvTypes_values = [VSN_Conv_Classified_Dict[key] for key in ConvTypes]
Datasets_to_ConvTypes_values.extend([Relevant_Conv_Classified_Dict[key] for key in ConvTypes])
Dataset_to_ConvTypes_MapSource = [0, 0, 0, 0,
                                  1, 1, 1, 1]
Dataset_to_ConvTypes_MapDest = [2,3,4,5,
                                2,3,4,5]
ConvTypes_to_UserTypes_pre_values = [VSN_Answer[key] for key in ConvTypes]
ConvTypes_to_UserTypes_pre_values.extend([Relevant_Answer[key] for key in ConvTypes])

ConvTypes_to_UserTypes_values=list()
for pair in ConvTypes_to_UserTypes_pre_values:
    ConvTypes_to_UserTypes_values.extend(pair)

from Visualize import Sankey_Diagram
Sankey_Values = Datasets_to_ConvTypes_values
Sankey_Values.extend(ConvTypes_to_UserTypes_values)

Sankey_Labels = Datasets
Sankey_Labels.extend(ConvTypes)
Sankey_Labels.extend(UserTypes)

Sankey_OutMap = Dataset_to_ConvTypes_MapSource
Sankey_OutMap.extend([2,2,3,3,4,4,5,5,2,2,3,3,4,4,5,5]) # Sources for ConvTypes_to_UserTypes_values

Sankey_InMap = Dataset_to_ConvTypes_MapDest
Sankey_InMap.extend([6,7,6,7,6,7,6,7,6,7,6,7,6,7,6,7]) # Destinations for ConvTypes_to_UserTypes_values

Sankey_Colormap =[0, 0, 0, 0, 1, 1, 1, 1, 0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]

fig = Sankey_Diagram(Sankey_Labels,Sankey_OutMap,Sankey_InMap,Sankey_Values,Sankey_Colormap)
fig.show
Sankey_Object = fig.data[0]

##################################
#Now for the Multisplit Version: #
##################################

Datasets = ['VSN Members','Relevant Conversations']
ConvTypes = list(VSN_Conv_Classified_Dict.keys())
UserTypes = ['Includes Individuals', 'Includes Other', 'Experts, Government, and Nonproft / Research Organizations Only']


Datasets_to_ConvTypes_values = [VSN_Conv_Classified_Dict[key] for key in ConvTypes]
Datasets_to_ConvTypes_values.extend([Relevant_Conv_Classified_Dict[key] for key in ConvTypes])
Dataset_to_ConvTypes_MapSource = [0, 0, 0, 0,
                                  1, 1, 1, 1]
Dataset_to_ConvTypes_MapDest = [2,3,4,5,
                                2,3,4,5]


ConvTypes_to_UserTypes_pre_values = [VSN_Multisplit_Answer[key] for key in ConvTypes]
ConvTypes_to_UserTypes_pre_values.extend([Relevant_Multisplit_Answer[key] for key in ConvTypes])

ConvTypes_to_UserTypes_values=list()
for pair in ConvTypes_to_UserTypes_pre_values:
    ConvTypes_to_UserTypes_values.extend(pair)

from Visualize import Sankey_Diagram
Sankey_Values = Datasets_to_ConvTypes_values.copy()
Sankey_Values.extend(ConvTypes_to_UserTypes_values)

Sankey_Labels = Datasets.copy()
Sankey_Labels.extend(ConvTypes)
Sankey_Labels.extend(UserTypes)

Sankey_OutMap = Dataset_to_ConvTypes_MapSource.copy()
Sankey_OutMap.extend([2,2,2,3,3,3,4,4,4,5,5,5,2,2,2,3,3,3,4,4,4,5,5,5]) # Sources for ConvTypes_to_UserTypes_values

Sankey_InMap = Dataset_to_ConvTypes_MapDest.copy()
Sankey_InMap.extend([6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8]) # Destinations for ConvTypes_to_UserTypes_values

Sankey_Colormap =[0, 0, 0, 0, 1, 1, 1, 1, 0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1]

fig = Sankey_Diagram(Sankey_Labels,Sankey_OutMap,Sankey_InMap,Sankey_Values,Sankey_Colormap)
fig.show
Sankey_Object = fig.data[0]


#
# len(Sankey_Labels)
# UserTypes = ['Includes Individuals", "Organizations and Experts Only']
#
# Sankey_Diagram(['VSN Members','Relevant Conversations',
#                      'Monologue','Reply','Dialogue','Multilogue',
#                      'Organization', 'Expert','Other'],
#                     [0, 0, 0, 0, 1, 1, 1, 1,
#                      2,2,2,3,3,3,4,4,4,5,5,5,2,2,2,3,3,3,4,4,4,5,5,5],
#                     [2,3,4,5,2,3,4,5,
#                      6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8],
#                     [79, 1197, 442, 108, 86, 1308, 546, 487,
#                      50,20,4,800,200,197,300,120,22,60,30,18,40,30,16,1000,200,108,200,300,46,200,220,67],
#                     [0, 0, 0, 0, 1, 1, 1, 1, 0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1])


# from Visualize import Sankey_Diagram
#
# Visual = Sankey_Diagram(['VSN Members','Relevant Conversations','Monologue','Reply','Dialogue','Multilogue'], [0, 0, 0, 0, 1, 1, 1, 1], [2,3,4,5,2,3,4,5], [79, 1197, 442, 108, 86, 1308, 546, 487])

# Sankey diagram should be expanded to a third column with who was involved in the conversations. Now done.
#
# # Fake Data:
# PPLType = ['Organization', 'Expert','Other', 'Etc']
# From = [2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5]
# To = [6,6,6,6,6,6,6,6,7,7,7,7,7,7,7,7,8,8,8,8,8,8,8,8,9,9,9,9,9,9,9,9]
# Values = [34, 23, 900, 300, 300,
#           68, 40, 405, 243, 184,
#           1,1,1,1,1,
#           1,1,1,1,1,
#           0,0,0,0,
#           0,0,0,0,
#           1,1,1,1,
#           0,0,0,0]
#
# This works, but the numbers are wrongly set up. Hmmm.
# Sankey_Diagram(['VSN Members','Relevant Conversations',
#                      'Monologue','Reply','Dialogue','Multilogue',
#                      'Organization', 'Expert','Other'],
#                     [0, 0, 0, 0, 1, 1, 1, 1,
#                      2,2,2,3,3,3,4,4,4,5,5,5,2,2,2,3,3,3,4,4,4,5,5,5],
#                     [2,3,4,5,2,3,4,5,
#                      6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8,6,7,8],
#                     [79, 1197, 442, 108, 86, 1308, 546, 487,
#                      50,20,4,800,200,197,300,120,22,60,30,18,40,30,16,1000,200,108,200,300,46,200,220,67],
#                     [0, 0, 0, 0, 1, 1, 1, 1, 0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1])
#
# # 79, 1197, 442, 108, \
# # 86, 1308, 546, 487,
# # 170, 2600, 1000, 590
#
# # 34, 23, 900, 300, 300, 68, 40, 405, 243, 184, 1,1,1,1,1, 1,1,1,1,1, 0,0,0,0, 1,1,1,1],

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
