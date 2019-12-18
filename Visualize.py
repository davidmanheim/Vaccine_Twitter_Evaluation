import networkx as nx
import json
import time


# From: https://stackoverflow.com/questions/17381006/large-graph-visualization-with-python-and-networkx, User Vikram -
def save_graph(graph, file_name):
    import matplotlib.pyplot as plt
    import numpy as np

    # initialze Figure
    plt.figure(num=None, figsize=(40, 40), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos, edge_color="green")
    nx.draw_networkx_labels(graph, pos)

    cut = 1
    xmax = cut * max(xx for xx, yy in pos.values()) - 0.05
    ymax = cut * max(yy for xx, yy in pos.values()) - 0.05
    xmin = cut * min(xx for xx, yy in pos.values()) + 0.05
    ymin = cut * min(yy for xx, yy in pos.values()) + 0.05
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    if False:
        pos_y_wide = pos.copy()
        for key in pos_y_wide:
            pos_y_wide[key][1] = pos_y_wide[key][1] * 1.1

    plt.savefig(file_name, bbox_inches="tight")
    # pylab.close()
    del fig


def Follower_In_Set_Graphing(Userlist_File='Updating_User_List_Retrieved_Followers.json'):
    Follower_Network = nx.DiGraph()

    print("Get User List")
    f = open(Userlist_File, 'r')
    # Follower_Entries = list()
    # print(line)
    Keynode_List = json.loads(f.readline())
    #User_ID = Follower_Entries[0]
    # print(User_ID)
    for user in Keynode_List:
        Follower_Network.add_node(user)
    f.close()

    print("Get Following Data")
    f = open('Follower_data.json', 'r')
    for line in f:
        # print(line)
        Follower_Entries = json.loads(line)
        # print(Follower_Entries)
        for id in Follower_Entries[2]:
            if Follower_Entries[1] == "Following":
                if id in Keynode_List:
                    Follower_Network.add_edge(Follower_Entries[0], id)
            elif Follower_Entries[1] == "FollowedBy":
                if id in Keynode_List:
                    Follower_Network.add_edge(id,Follower_Entries[0])
            else:
                print("BAD!")
    f.close()

    #Assuming that the graph g has nodes and edges entered
    # Sub = Follower_Network.subgraph(Keynode_List).copy()

    #for n in Sub.nodes:
    #    print(n)

    return(Follower_Network)


def tweet_is_reply(tweet):
    output = 0
    if tweet["in_reply_to_status_id"] is not None:
        output = output + 1
    if "quoted_status_id" in tweet:
        output = output + 2
    return(output)

from Tweet_File_Analysis_Functions import DateRange, Get_FileList_Of_JSON_Files
import time

def Threads_vs_Nonthreads():
    # Get Data on which threads and discussion belong to whom IN THE USER LIST, not for all items in threads:
    Tweet_data_all_files = Get_FileList_Of_JSON_Files("data", "Tweets_by_")
    # Need only files of form: "Tweets_by_2687637427_back_to_2008..."

    # Which ones are WHO_VSN members?
    f = open('Data\\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json')
    # List of Members
    list_from_file = json.loads(f.readline())
    Member_List = [User['id'] for User in list_from_file]
    f.close()

    # from Tweet_File_Analysis_Functions import tweet_is_reply

    for UserID in Member_List:
        # There will be a file for each user!
        Userfile=[file for file in Tweet_data_all_files if str(UserID) in file]
        print("Check file for user", UserID)
        if len(Userfile) == 1:
            Userfile = Userfile[0]
        else:
            continue
        with open("Data\\Tweet_Classify_VSN_Members_Only.json", "a") as outfile:
            with open(Userfile, 'r') as f:
                UserTweetCategories=list()
                for tweet_text in f:
                    tweet = json.loads(tweet_text)
                    Check = True
                    ts = time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    if ts < time.strptime(DateRange[0], '%b %d %H:%M:%S %Y'):
                        Check = False
                    elif ts > time.strptime(DateRange[1], '%b %d %H:%M:%S %Y'):
                        Check = False
                    type=tweet_is_reply(tweet)
                    if type == 0:
                        category = (tweet["id"], "Nonreply", UserID, "WHO_VSN Member")
                    elif type == 1:
                        category = (tweet["id"], "Reply", UserID, "WHO_VSN Member")
                    elif type == 2:
                        category = (tweet["id"], "Quote", UserID, "WHO_VSN Member")
                    elif type == 3:
                        category = (tweet["id"], "Reply+Quote", UserID, "WHO_VSN Member")
                    UserTweetCategories.append(category)
            outfile.write(json.dumps(UserTweetCategories))
            outfile.write('\n')
        outfile.close()

#Threads_vs_Nonthreads()

def Thread_vs_NonThread_Summary():
    Summary = {}
    Summary["Total"] = {'Nonreply': 0, 'Reply': 0, 'Quote': 0, "Reply+Quote": 0}
    with open("Data\\Tweet_Classify_VSN_Members_Only.json", "r") as categories:
        #Did this filter by date yet? Need to regenerate it to make sure it's only 2018. Done.
        for line in categories:
            tweetlist = json.loads(line)
            if tweetlist[0][2] not in Summary.keys():
                Summary[tweetlist[0][2]] = {'Nonreply':0, 'Reply':0, 'Quote':0, "Reply+Quote":0}
            for tweetcat in tweetlist:
                    Summary[tweetcat[2]][tweetcat[1]] = Summary[tweetcat[2]][tweetcat[1]] + 1
                    Summary["Total"][tweetcat[1]] = Summary["Total"][tweetcat[1]] + 1
    return(Summary)

# Do some checking.
if False:
    a = Thread_vs_NonThread_Summary()
    a.pop("Total",None)
    most = 0
    least = 100000000
    for u in a:
        if u!='Total':
            t = a[u]['Nonreply'] + a[u]['Reply'] + a[u]['Quote'] + a[u]['Reply+Quote']
            if t > most:
                most=t
                m_user = u
            if t < least:
                least = t
                l_user = u
    len(a.keys())


def User_TweetCounts():
    User_TweetCounts = {}
    # Count total number of tweets by VSN members.
    with open("Data\\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json", "r") as users:
        # Did this filter by date yet? Need to regenerate it to make sure it's only 2018. Done.
        userlist = json.loads(users.readline())
        for user in userlist:
            if "statuses_count" in user.keys():
                User_TweetCounts[user['id']]=user["statuses_count"]
    return(User_TweetCounts)




def TypePieChart(dict):
    Labels = dict.keys()
    Values = [dict[key] for key in dict.keys()]
    plt.pie(Values,None,Labels, autopct='%1.1f%%')


def MultiNestPieChart(dict,sizedict=None):
    import matplotlib.pyplot as plt
    from math import log
    count = len(dict)

    rows = 6

    if count <= 47:  # 6 rows
        rows = 5
    if count <= 34:  # 5 rows
        rows = 4
    if count <= 24:  # 4 rows
        rows = 3
    if count <= 12:  # 3 rows
        rows = 2
    if count<=6: #2 rows
        rows = 1

    cols = int(count / rows)
    if count % rows != 0:
        cols=cols+1

    # Get biggest item, so I can scale later:
    if sizedict is not None:
        biggest = max(sizedict.values())

    #plt.figure(num=None, figsize=(rows, cols))
    itemnum=1
    plt.rcParams['figure.dpi']=600
    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=1.75, hspace=.3)
    #dolegend=True
    for item in dict:
        #if(dolegend):
            #plt.legend(loc='lower left', fontsize=7, bbox_to_anchor=(0., 1.02, 1., .102), labels=dict[item].keys())
            #dolegend=False
        ax = plt.subplot(rows, cols, itemnum)
        # plt.figure(num=None, figsize=(0.7,0.7))
        plt.axis('off')
        if sizedict is not None:
            if item in sizedict:
                rad =log(sizedict[item]) / log(biggest)
            else:
                rad = 2 # Too big, shows obvious error.
        else:
            rad = 1
        plt.pie(dict[item].values(), labels=None, frame=True, radius=rad)
        #if itemnum==1:
            #plt.legend(loc='lower right', fontsize=7, bbox_to_anchor=(.1, .1))
        itemnum = itemnum + 1
    plt.show()

    # I'd like to have a single legend, but how do I place it correctly?
    # Just make a new plot and steal that one:
    # plt.pie(dict[item].values(), labels=dict[item].keys(), frame=True, radius=0.0001)
    # plt.axis('off')
    # plt.legend()
    # (This is a bad way to do this.)



if False:
    D = Thread_vs_NonThread_Summary()
    D.pop('Total', None)
    MultiNestPieChart(D)


def HistChart(dict, cutoff=None):
    if cutoff is not None:
        X = [key for key in dict.keys() if dict[key] >= cutoff]
        Weights = [dict[key] for key in dict.keys() if dict[key] >= cutoff]
    else:
        X = dict.keys()
        Weights = [dict[key] for key in dict.keys()]
    plt.hist(X,weights=Weights)

def Graph_Degree_Histogram(G):
    import collections
    import matplotlib.pyplot as plt
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    # print "Degree sequence", degree_sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    pyl.bar(deg, cnt, width=0.80, color='b')

    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d + 0.4 for d in deg])
    ax.set_xticklabels(deg)



follower=False #True

if follower == True:
    # Follower Graph
    F_Graph = Follower_In_Set_Graphing()

    #Remove strays:
    #F_Graph.remove_nodes_from([n for n in F_Graph if F_Graph.degree(n)<6])

    print("Get Relabel Data")
    f = open('Data\\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json')
    rename_dict = dict()
    list_from_file=json.loads(f.readline())
    for User in list_from_file:
        rename_dict[User['id']] = User['screen_name']
    f.close()

    Full_Subgraph = False

    if Full_Subgraph:

        print("Save Graph")
        save_graph(nx.relabel_nodes(F_Graph, rename_dict), ("Follower_graph" + str(time.time()) + ".pdf"))
        print("Save VSN Only Graph")

    WHO_VSN_Graph = True
    if WHO_VSN_Graph:
        F_SubGraph = nx.subgraph(F_Graph.copy(), [User['id'] for User in list_from_file])
        save_graph(nx.relabel_nodes(F_SubGraph, rename_dict), ("WHO_VSN Only follower graph " + str(time.time()) + ".pdf"))
    #plt.savefig("WHO_VSN Only follower graph - FINAL " + str(time.time()) + ".pdf", bbox_inches="tight")
    # Runs out of ram for the graph... :(
    # nx.write_graphml(thread_graphing(), path="Test_Replies.GraphML")

    # Widen positions on the graph y-axis:
    # ?

    Graph_Degree_Histogram = False
    if Graph_Degree_Histogram == True:
        Graph_Degree_Histogram(Follower_Network)

#nx.spring_layout(Follower_Network)
#nx.draw_networkx(Follower_Network)


def thread_graphing(input_file='data//Thread_Tweet_Structure_at_1563435934.7016308.json'):
    Threads_Forest = nx.DiGraph()

    # Thread_List = list()

    f = open(input_file, 'r')
    Full_data = json.loads(f.readline())
    for reply in Full_data: # Node
        Threads_Forest.add_node(reply[0], user=reply[2])
        Threads_Forest.add_node(reply[1], user=reply[3])
        Threads_Forest.add_edge(reply[0], reply[1], type=reply[4])
    # print(len(Full_data))

    return(Threads_Forest)

# Given the thread forest, we have some things to do...


def Get_Threads():
    print("Get Threads Data")
    Thread_Graphs = thread_graphing()
    Undir_Threads = Thread_Graphs.to_undirected()
    Thread_Sets = nx.connected_components(Undir_Threads)
    # Size_Hist = [len(c) for c in sorted(Thread_Sets, key=len, reverse=True)]

    # test=Thread_Sets.__next__()

    # I need to classify threads by length and participants
    Thread_Sets = nx.connected_components(Undir_Threads)
    Thread_Forest = [nx.subgraph(Thread_Graphs, subset) for subset in Thread_Sets]
    # The Forest is a list of directed Graphs.
    return Thread_Forest, Thread_Sets

def User_Class(user, dict=None, key="Heuristic Class"):
    if dict is None:
        with open("data\Classified_Users_With_BotOrNot_One_line.json", 'r') as r:
            Users_Classified = json.loads(r.readline())
            r.close()
        dict = Users_Classified
    if str(user) in dict.keys():
        if key in dict[str(user)].keys():
            return(str(dict[str(user)][key]))
        else:
            return("Unknown")
    else:
        return ("Unknown")

def Users_Classlist(tree, dict=None, key="Heuristic Class", Details=False):
    userset = set()
    usertypeset = set()
    for node in tree.nodes:
        userset.add(tree.nodes[node]['user'])
    for user in userset:
        type = User_Class(user)
        if type is not None:
            usertypeset.add(type)
        else:
            usertypeset.add("Unknown")
    if Details:
        return str(sorted(usertypeset)), str(len(userset))
    elif len(usertypeset) > 0:
        return str(sorted(usertypeset))
    else:
        return None


def Thread_Types(Thread_Forest, Users_Classified, Details=False):
    #For each tree in the forest, I need to find the structure, in terms of users and replies.
    TreeClassifyGram = {}
    type = None
    for tree in Thread_Forest:
        if Details:
            usertypeset, users = Users_Classlist(tree, dict=Users_Classified, key="Heuristic Class", Details=Details)
            type = str(len(tree)) + " tweets, " + users + " users " + usertypeset
        else:
            type = Users_Classlist(tree, dict=Users_Classified, key="Heuristic Class", Details=Details)
        if type in TreeClassifyGram.keys():
            TreeClassifyGram[type] = TreeClassifyGram[type] + 1
        else:
            TreeClassifyGram[type] = 1
    return(TreeClassifyGram)

def Thread_Metrics(plotting=False, thread=False, Thread_Forest=None):
    if Thread_Forest==None:
        Thread_Forest, Thread_Sets = Get_Threads()

    if thread==False:
        #For each tree in the forest, I need to find the structure, in terms of users and replies.
        TypeSet = set()
        TreeClassifyGram = {}
        TreeClassifyGram_WithTypes = {}
        for tree in Thread_Forest:
            userset = set()
            type = None
            for node in tree.nodes:
                userset.add(tree.nodes[node]['user'])
            types = nx.get_edge_attributes(tree,'type').values()

            Type = types.__iter__().__next__()
            if len(types) == 1:
                TypeSet.add(Type)
            else:
                Type = "Mixed"
            size = len(tree)
            users = len(userset)
            entry = str(size) + " tweets, " + str(users) + " users"
            Typeentry = str(size) + " tweets, " + str(users) + " users " + Type
            if entry in TreeClassifyGram.keys():
                TreeClassifyGram[entry] = TreeClassifyGram[entry] + 1
            else:
                TreeClassifyGram[entry] = 1
            if Typeentry in TreeClassifyGram_WithTypes.keys():
                TreeClassifyGram_WithTypes[Typeentry] = TreeClassifyGram_WithTypes[Typeentry] + 1
            else:
                TreeClassifyGram_WithTypes[Typeentry] = 1
    if plotting==False:
        return(TreeClassifyGram_WithTypes)

    # VSN: {'13 tweets, 3 users Mixed': 1, '2 tweets, 2 users Reply': 648, '9 tweets, 2 users Mixed': 2, '4 tweets, 2 users Mixed': 85, '3 tweets, 2 users Mixed': 211, '11 tweets, 4 users Mixed': 2, '8 tweets, 3 users Mixed': 5, '4 tweets, 3 users Mixed': 57, '5 tweets, 2 users Mixed': 33, '3 tweets, 3 users Mixed': 160, '5 tweets, 3 users Mixed': 36, '6 tweets, 5 users Mixed': 5, '6 tweets, 2 users Mixed': 11, '6 tweets, 3 users Mixed': 15, '7 tweets, 3 users Mixed': 13, '6 tweets, 4 users Mixed': 18, '4 tweets, 4 users Mixed': 33, '7 tweets, 2 users Mixed': 5, '2 tweets, 2 users Quote': 207, '23 tweets, 19 users Mixed': 1, '7 tweets, 7 users Mixed': 4, '11 tweets, 9 users Mixed': 2, '17 tweets, 3 users Mixed': 1, '12 tweets, 4 users Mixed': 3, '5 tweets, 4 users Mixed': 12, '9 tweets, 3 users Mixed': 3, '9 tweets, 5 users Mixed': 4, '9 tweets, 6 users Mixed': 3, '2 tweets, 1 users Reply': 59, '34 tweets, 6 users Mixed': 1, '8 tweets, 4 users Mixed': 4, '10 tweets, 4 users Mixed': 6, '7 tweets, 4 users Mixed': 8, '12 tweets, 3 users Mixed': 1, '13 tweets, 5 users Mixed': 1, '10 tweets, 6 users Mixed': 2, '8 tweets, 1 users Mixed': 5, '9 tweets, 4 users Mixed': 3, '11 tweets, 5 users Mixed': 6, '32 tweets, 1 users Mixed': 1, '18 tweets, 5 users Mixed': 1, '12 tweets, 9 users Mixed': 2, '17 tweets, 4 users Mixed': 1, '10 tweets, 1 users Mixed': 2, '5 tweets, 5 users Mixed': 10, '12 tweets, 7 users Mixed': 1, '8 tweets, 5 users Mixed': 4, '26 tweets, 6 users Mixed': 1, '3 tweets, 1 users Mixed': 41, '20 tweets, 5 users Mixed': 1, '50 tweets, 27 users Mixed': 1, '2 tweets, 1 users Quote': 5, '19 tweets, 4 users Mixed': 1, '11 tweets, 3 users Mixed': 2, '8 tweets, 6 users Mixed': 2, '6 tweets, 1 users Mixed': 5, '6 tweets, 6 users Mixed': 2, '22 tweets, 6 users Mixed': 1, '10 tweets, 3 users Mixed': 4, '20 tweets, 8 users Mixed': 1, '9 tweets, 7 users Mixed': 1, '116 tweets, 17 users Mixed': 1, '5 tweets, 1 users Mixed': 7, '7 tweets, 5 users Mixed': 3, '58 tweets, 12 users Mixed': 1, '8 tweets, 2 users Mixed': 3, '4 tweets, 1 users Mixed': 11, '35 tweets, 12 users Mixed': 1, '11 tweets, 1 users Mixed': 2, '15 tweets, 8 users Mixed': 1, '11 tweets, 6 users Mixed': 1, '7 tweets, 1 users Mixed': 5, '34 tweets, 3 users Mixed': 1, '8 tweets, 7 users Mixed': 2, '10 tweets, 2 users Mixed': 2, '10 tweets, 5 users Mixed': 2, '15 tweets, 7 users Mixed': 1, '52 tweets, 52 users Mixed': 1, '24 tweets, 4 users Mixed': 1, '14 tweets, 7 users Mixed': 1, '7 tweets, 6 users Mixed': 1, '59 tweets, 24 users Mixed': 1, '30 tweets, 8 users Mixed': 1, '18 tweets, 7 users Mixed': 1, '17 tweets, 6 users Mixed': 1, '41 tweets, 8 users Mixed': 1, '10 tweets, 7 users Mixed': 1, '13 tweets, 6 users Mixed': 1, '11 tweets, 2 users Mixed': 1, '13 tweets, 10 users Mixed': 1, '14 tweets, 8 users Mixed': 1, '16 tweets, 5 users Mixed': 1, '11 tweets, 8 users Mixed': 1}
    # Relevant: {'47 tweets, 6 users Mixed': 1, '8 tweets, 4 users Mixed': 15, '3 tweets, 2 users Mixed': 158, '2 tweets, 2 users Quote': 312, '2 tweets, 2 users Reply': 434, '4 tweets, 3 users Mixed': 89, '8 tweets, 3 users Mixed': 17, '6 tweets, 6 users Mixed': 11, '51 tweets, 12 users Mixed': 1, '3 tweets, 3 users Mixed': 209, '9 tweets, 3 users Mixed': 15, '173 tweets, 1 users Mixed': 1, '5 tweets, 2 users Mixed': 35, '69 tweets, 28 users Mixed': 1, '14 tweets, 6 users Mixed': 5, '2 tweets, 1 users Reply': 55, '47 tweets, 2 users Mixed': 1, '7 tweets, 4 users Mixed': 29, '7 tweets, 3 users Mixed': 20, '6 tweets, 5 users Mixed': 12, '3 tweets, 1 users Mixed': 25, '7 tweets, 2 users Mixed': 14, '8 tweets, 5 users Mixed': 10, '4 tweets, 4 users Mixed': 61, '11 tweets, 5 users Mixed': 11, '4 tweets, 1 users Mixed': 14, '4 tweets, 2 users Mixed': 72, '16 tweets, 4 users Mixed': 2, '15 tweets, 2 users Mixed': 2, '29 tweets, 7 users Mixed': 2, '9 tweets, 4 users Mixed': 11, '5 tweets, 3 users Mixed': 52, '11 tweets, 3 users Mixed': 11, '6 tweets, 1 users Mixed': 5, '14 tweets, 4 users Mixed': 5, '35 tweets, 7 users Mixed': 1, '6 tweets, 3 users Mixed': 28, '18 tweets, 5 users Mixed': 5, '12 tweets, 5 users Mixed': 8, '19 tweets, 6 users Mixed': 3, '13 tweets, 2 users Mixed': 2, '23 tweets, 5 users Mixed': 5, '9 tweets, 5 users Mixed': 9, '10 tweets, 5 users Mixed': 8, '5 tweets, 4 users Mixed': 40, '30 tweets, 5 users Mixed': 3, '7 tweets, 6 users Mixed': 8, '25 tweets, 5 users Mixed': 1, '5 tweets, 1 users Mixed': 9, '6 tweets, 2 users Mixed': 17, '17 tweets, 6 users Mixed': 3, '59 tweets, 16 users Mixed': 1, '20 tweets, 5 users Mixed': 1, '50 tweets, 27 users Mixed': 1, '16 tweets, 5 users Mixed': 4, '2 tweets, 1 users Quote': 27, '33 tweets, 1 users Mixed': 1, '7 tweets, 5 users Mixed': 19, '12 tweets, 6 users Mixed': 4, '6 tweets, 4 users Mixed': 35, '53 tweets, 6 users Mixed': 1, '24 tweets, 1 users Mixed': 2, '13 tweets, 7 users Mixed': 6, '5 tweets, 5 users Mixed': 19, '7 tweets, 7 users Mixed': 3, '19 tweets, 2 users Mixed': 2, '12 tweets, 2 users Mixed': 4, '8 tweets, 6 users Mixed': 5, '29 tweets, 4 users Mixed': 1, '10 tweets, 3 users Mixed': 13, '14 tweets, 13 users Mixed': 1, '44 tweets, 12 users Mixed': 1, '18 tweets, 1 users Mixed': 1, '19 tweets, 1 users Mixed': 1, '18 tweets, 6 users Mixed': 2, '22 tweets, 11 users Mixed': 1, '14 tweets, 5 users Mixed': 4, '34 tweets, 9 users Mixed': 1, '9 tweets, 1 users Mixed': 6, '16 tweets, 2 users Mixed': 2, '57 tweets, 13 users Mixed': 1, '36 tweets, 10 users Mixed': 1, '116 tweets, 20 users Mixed': 1, '8 tweets, 2 users Mixed': 7, '56 tweets, 2 users Mixed': 1, '8 tweets, 1 users Mixed': 5, '22 tweets, 1 users Mixed': 1, '15 tweets, 1 users Mixed': 1, '11 tweets, 4 users Mixed': 9, '8 tweets, 8 users Mixed': 2, '13 tweets, 8 users Mixed': 1, '31 tweets, 10 users Mixed': 1, '9 tweets, 8 users Mixed': 2, '9 tweets, 2 users Mixed': 5, '7 tweets, 1 users Mixed': 5, '74 tweets, 23 users Mixed': 1, '10 tweets, 6 users Mixed': 5, '11 tweets, 10 users Mixed': 1, '40 tweets, 5 users Mixed': 1, '11 tweets, 1 users Mixed': 4, '21 tweets, 9 users Mixed': 1, '12 tweets, 9 users Mixed': 2, '25 tweets, 4 users Mixed': 1, '10 tweets, 2 users Mixed': 3, '12 tweets, 4 users Mixed': 7, '12 tweets, 3 users Mixed': 7, '96 tweets, 18 users Mixed': 1, '10 tweets, 4 users Mixed': 8, '52 tweets, 4 users Mixed': 1, '128 tweets, 7 users Mixed': 1, '53 tweets, 7 users Mixed': 1, '25 tweets, 3 users Mixed': 1, '15 tweets, 7 users Mixed': 2, '167 tweets, 5 users Mixed': 1, '14 tweets, 2 users Mixed': 3, '40 tweets, 3 users Mixed': 1, '13 tweets, 3 users Mixed': 5, '23 tweets, 3 users Mixed': 1, '9 tweets, 9 users Mixed': 2, '27 tweets, 6 users Mixed': 1, '12 tweets, 7 users Mixed': 2, '9 tweets, 6 users Mixed': 4, '20 tweets, 8 users Mixed': 1, '24 tweets, 10 users Mixed': 2, '25 tweets, 2 users Mixed': 1, '116 tweets, 17 users Mixed': 1, '32 tweets, 9 users Mixed': 1, '197 tweets, 17 users Mixed': 1, '10 tweets, 7 users Mixed': 3, '32 tweets, 7 users Mixed': 1, '18 tweets, 4 users Mixed': 3, '32 tweets, 3 users Mixed': 2, '40 tweets, 7 users Mixed': 1, '20 tweets, 6 users Mixed': 2, '76 tweets, 35 users Mixed': 1, '1404 tweets, 138 users Mixed': 1, '32 tweets, 5 users Mixed': 1, '61 tweets, 14 users Mixed': 1, '45 tweets, 12 users Mixed': 1, '29 tweets, 9 users Mixed': 4, '15 tweets, 4 users Mixed': 4, '62 tweets, 20 users Mixed': 1, '11 tweets, 8 users Mixed': 3, '23 tweets, 7 users Mixed': 3, '21 tweets, 5 users Mixed': 1, '24 tweets, 9 users Mixed': 2, '55 tweets, 11 users Mixed': 1, '30 tweets, 11 users Mixed': 2, '22 tweets, 6 users Mixed': 1, '89 tweets, 23 users Mixed': 1, '188 tweets, 37 users Mixed': 1, '24 tweets, 6 users Mixed': 3, '47 tweets, 11 users Mixed': 1, '41 tweets, 7 users Mixed': 1, '33 tweets, 6 users Mixed': 2, '19 tweets, 9 users Mixed': 1, '26 tweets, 9 users Mixed': 1, '25 tweets, 10 users Mixed': 1, '80 tweets, 15 users Mixed': 2, '58 tweets, 12 users Mixed': 1, '109 tweets, 19 users Mixed': 1, '14 tweets, 3 users Mixed': 2, '17 tweets, 2 users Mixed': 1, '14 tweets, 8 users Mixed': 2, '63 tweets, 4 users Mixed': 1, '50 tweets, 15 users Mixed': 1, '34 tweets, 6 users Mixed': 1, '43 tweets, 11 users Mixed': 1, '84 tweets, 6 users Mixed': 1, '18 tweets, 7 users Mixed': 2, '28 tweets, 7 users Mixed': 1, '38 tweets, 4 users Mixed': 2, '16 tweets, 6 users Mixed': 3, '137 tweets, 22 users Mixed': 1, '12 tweets, 11 users Mixed': 1, '13 tweets, 4 users Mixed': 4, '21 tweets, 6 users Mixed': 2, '24 tweets, 4 users Mixed': 3, '15 tweets, 5 users Mixed': 2, '31 tweets, 8 users Mixed': 2, '35 tweets, 12 users Mixed': 1, '69 tweets, 21 users Mixed': 1, '42 tweets, 10 users Mixed': 2, '29 tweets, 5 users Mixed': 1, '60 tweets, 14 users Mixed': 1, '15 tweets, 6 users Mixed': 7, '36 tweets, 13 users Mixed': 1, '17 tweets, 17 users Mixed': 1, '27 tweets, 4 users Mixed': 1, '54 tweets, 11 users Mixed': 1, '13 tweets, 5 users Mixed': 4, '25 tweets, 7 users Mixed': 1, '47 tweets, 13 users Mixed': 1, '15 tweets, 8 users Mixed': 1, '40 tweets, 9 users Mixed': 1, '14 tweets, 7 users Mixed': 2, '12 tweets, 8 users Mixed': 2, '75 tweets, 1 users Mixed': 1, '141 tweets, 14 users Mixed': 1, '22 tweets, 7 users Mixed': 1, '46 tweets, 7 users Mixed': 4, '41 tweets, 12 users Mixed': 1, '45 tweets, 3 users Mixed': 1, '20 tweets, 4 users Mixed': 3, '20 tweets, 14 users Mixed': 1, '19 tweets, 7 users Mixed': 1, '24 tweets, 11 users Mixed': 1, '11 tweets, 6 users Mixed': 6, '17 tweets, 9 users Mixed': 2, '225 tweets, 28 users Mixed': 1, '33 tweets, 25 users Mixed': 1, '8 tweets, 7 users Mixed': 4, '23 tweets, 10 users Mixed': 1, '66 tweets, 14 users Mixed': 1, '464 tweets, 32 users Mixed': 1, '33 tweets, 7 users Mixed': 1, '49 tweets, 9 users Mixed': 1, '17 tweets, 7 users Mixed': 1, '22 tweets, 5 users Mixed': 1, '11 tweets, 9 users Mixed': 1, '32 tweets, 14 users Mixed': 1, '38 tweets, 12 users Mixed': 1, '45 tweets, 17 users Mixed': 1, '16 tweets, 10 users Mixed': 1, '19 tweets, 12 users Mixed': 2, '17 tweets, 11 users Mixed': 2, '196 tweets, 34 users Mixed': 1, '13 tweets, 11 users Mixed': 1, '264 tweets, 28 users Mixed': 1, '28 tweets, 6 users Mixed': 1, '37 tweets, 12 users Mixed': 1, '22 tweets, 9 users Mixed': 1, '21 tweets, 10 users Mixed': 1, '50 tweets, 19 users Mixed': 1, '11 tweets, 7 users Mixed': 2, '34 tweets, 3 users Mixed': 1, '76 tweets, 11 users Mixed': 1, '69 tweets, 11 users Mixed': 1, '41 tweets, 14 users Mixed': 1, '16 tweets, 7 users Mixed': 2, '63 tweets, 13 users Mixed': 1, '21 tweets, 7 users Mixed': 1, '51 tweets, 6 users Mixed': 1, '22 tweets, 8 users Mixed': 2, '19 tweets, 10 users Mixed': 1, '56 tweets, 22 users Mixed': 1, '25 tweets, 8 users Mixed': 1, '23 tweets, 9 users Mixed': 1, '44 tweets, 15 users Mixed': 1, '43 tweets, 9 users Mixed': 1, '45 tweets, 8 users Mixed': 1, '22 tweets, 2 users Mixed': 1, '26 tweets, 7 users Mixed': 1, '26 tweets, 6 users Mixed': 2, '39 tweets, 8 users Mixed': 1, '52 tweets, 10 users Mixed': 1, '39 tweets, 11 users Mixed': 1, '74 tweets, 27 users Mixed': 1, '48 tweets, 22 users Mixed': 1, '55 tweets, 10 users Mixed': 1, '13 tweets, 6 users Mixed': 1, '22 tweets, 3 users Mixed': 1, '438 tweets, 16 users Mixed': 1, '28 tweets, 8 users Mixed': 1, '49 tweets, 4 users Mixed': 1, '59 tweets, 15 users Mixed': 1, '48 tweets, 15 users Mixed': 1, '81 tweets, 2 users Mixed': 1, '17 tweets, 10 users Mixed': 1, '47 tweets, 10 users Mixed': 1, '44 tweets, 13 users Mixed': 1, '14 tweets, 1 users Mixed': 2, '122 tweets, 10 users Mixed': 1, '28 tweets, 19 users Mixed': 1, '69 tweets, 14 users Mixed': 1, '31 tweets, 25 users Mixed': 1, '24 tweets, 8 users Mixed': 1, '17 tweets, 4 users Mixed': 1, '28 tweets, 1 users Mixed': 1, '255 tweets, 32 users Mixed': 1, '146 tweets, 26 users Mixed': 1, '14 tweets, 12 users Mixed': 1, '37 tweets, 8 users Mixed': 1, '25 tweets, 1 users Mixed': 1, '18 tweets, 3 users Mixed': 3, '59 tweets, 19 users Mixed': 1, '40 tweets, 11 users Mixed': 1, '52 tweets, 14 users Mixed': 1, '72 tweets, 10 users Mixed': 1, '137 tweets, 11 users Mixed': 1, '20 tweets, 3 users Mixed': 2, '44 tweets, 4 users Mixed': 1, '20 tweets, 15 users Mixed': 1, '34 tweets, 15 users Mixed': 1, '13 tweets, 9 users Mixed': 1, '21 tweets, 3 users Mixed': 1, '10 tweets, 10 users Mixed': 1, '18 tweets, 13 users Mixed': 1, '362 tweets, 3 users Mixed': 1, '17 tweets, 3 users Mixed': 2, '10 tweets, 8 users Mixed': 1, '27 tweets, 10 users Mixed': 1, '38 tweets, 7 users Mixed': 1, '64 tweets, 11 users Mixed': 1, '48 tweets, 10 users Mixed': 1, '15 tweets, 3 users Mixed': 2, '100 tweets, 18 users Mixed': 1, '19 tweets, 4 users Mixed': 2, '82 tweets, 14 users Mixed': 1, '45 tweets, 7 users Mixed': 1, '39 tweets, 5 users Mixed': 1, '35 tweets, 6 users Mixed': 1, '182 tweets, 26 users Mixed': 1, '19 tweets, 5 users Mixed': 1, '33 tweets, 14 users Mixed': 1, '62 tweets, 14 users Mixed': 1, '68 tweets, 12 users Mixed': 1, '58 tweets, 10 users Mixed': 1, '21 tweets, 4 users Mixed': 1, '16 tweets, 3 users Mixed': 1, '33 tweets, 11 users Mixed': 1, '42 tweets, 8 users Mixed': 1, '34 tweets, 7 users Mixed': 1, '55 tweets, 8 users Mixed': 1, '57 tweets, 3 users Mixed': 1}

        # HistChart(TreeClassifyGram)
        import operator

        sorted_TreeClassifyGram = sorted(TreeClassifyGram.items(), key=operator.itemgetter(1), reverse=True)
        sorted_TreeTypeClassifyGram = sorted(TreeClassifyGram_WithTypes.items(), key=operator.itemgetter(1), reverse=True)

        # [('2 tweets, 2 users', 20701), ('3 tweets, 3 users', 5146), ('3 tweets, 2 users', 4443),
        # ('2 tweets, 1 users', 2334), ('4 tweets, 3 users', 1927), ('4 tweets, 2 users', 1248),
        # ('4 tweets, 4 users', 1240), ('5 tweets, 3 users', 1036), ('5 tweets, 2 users', 779),
        # ('5 tweets, 4 users', 670), ('3 tweets, 1 users', 575), ('6 tweets, 3 users', 534),
        # ('6 tweets, 4 users', 508), ('5 tweets, 5 users', 403), ('6 tweets, 2 users', 310),
        # ('4 tweets, 1 users', 301), ('7 tweets, 3 users', 299), ('7 tweets, 4 users', 294), ('6 tweets, 5 users', 231)
        # ... etc.

        # Quotes or Replies?
        # [('2 tweets, 2 users Reply', 11460), ('2 tweets, 2 users Quote', 9241), ('3 tweets, 3 users Mixed', 5146),
        # ('3 tweets, 2 users Mixed', 4443), ('4 tweets, 3 users Mixed', 1927), ('2 tweets, 1 users Reply', 1827),
        # ('4 tweets, 2 users Mixed', 1248), ('4 tweets, 4 users Mixed', 1240), ('5 tweets, 3 users Mixed', 1036),
        # ('5 tweets, 2 users Mixed', 779), ('5 tweets, 4 users Mixed', 670), ('3 tweets, 1 users Mixed', 575),
        # ('6 tweets, 3 users Mixed', 534), ('6 tweets, 4 users Mixed', 508), ('2 tweets, 1 users Quote', 507),
        # ... etc.

        Minitrees_2 = [Tree for Tree in Thread_Forest if len(Tree) == 2]
        Minitrees_3 = [Tree for Tree in Thread_Forest if len(Tree) == 3]





        if plotting:
            from numpy import histogram
            import matplotlib.pyplot as plt

            plt.hist([len(c) for c in sorted(nx.connected_components(Thread_Graphs), key=len, reverse=True)], bins=20)
            plt.yscale('log')
            plt.close()

            # Short Threads:
            plt.hist([len(c) for c in sorted(nx.connected_components(Thread_Graphs), key=len, reverse=True) if len(c)<20], bins=21)
            plt.yscale('log')
            #Note: This starts with only replies. Non-replies are a majority!

        Set_Users={}
        for Nodeset in Thread_Sets:
            Subgraph = Thread_Graphs.subgraph(Nodeset).copy()
            userlist=list()
            for node in Subgraph.nodes:
                u=Subgraph.node[node]['user']
                if u not in userlist:
                    userlist.append(u)
            number_users = len(userlist)
            if number_users in Set_Users.keys():
                Set_Users[number_users] = Set_Users[number_users] + 1
            else:
                Set_Users[number_users] = 1
        # 27,780 have two, 9,610 have three, etc.
        # Large sets (one example each) include: 110 users, 76 users, 64 users, 65 users.
        # There are two examples each of threads with 61, 44, and 28 users!


# Lightly changed from the source here: https://plot.ly/python/sankey-diagram/
def Sankey_Diagram(Labels, Source, Target, Values, ColorMap=None):
    import plotly.graph_objects as go
    from matplotlib import colors as colorlib
    from numpy import linspace

    from matplotlib import cm

    number_of_colors = len(Labels)
    color_prelist = [cm.Pastel1(n) for n in range(1, number_of_colors+2)]

    colorlist = ["rgb("+str(color_prelist[n][0])+","+str(color_prelist[n][1])+","+str(color_prelist[n][2])+")" for n in range(0,number_of_colors-1)]

    if ColorMap is not None:
        LinkColors = [["rgba("+str(color_prelist[n][0])+","+str(color_prelist[n][1])+","+str(color_prelist[n][2])+",0.5)" for n in range(0,number_of_colors-1)][i] for i in ColorMap]
    else:
        LinkColors = None
    # print([color for color in LinkColors])

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=Labels,
            color=colorlist #"blue"
        ),
        link=dict(
            source=Source,  # [0, 1, 0, 2, 3, 3],  # indices correspond to labels, eg A1, A2, A2, B1, ...
            target=Target,  #[2, 3, 3, 4, 4, 5],
            value=Values, #[8, 4, 2, 8, 4, 2],
            color=LinkColors
        ))])

    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    # fig.show()
    return fig


# Test = Sankey_Diagram(['a','b','c','d','e','f'], [0, 1, 0, 2, 3, 3], [2, 3, 3, 4, 4, 5], [8, 4, 2, 8, 4, 2])