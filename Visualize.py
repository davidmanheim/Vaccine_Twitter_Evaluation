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
        for line in categories:
            tweetlist = json.loads(line)
            if tweetlist[0][2] not in Summary.keys():
                Summary[tweetlist[0][2]] = {'Nonreply':0, 'Reply':0, 'Quote':0, "Reply+Quote":0}
            for tweetcat in tweetlist:
                    Summary[tweetcat[2]][tweetcat[1]] = Summary[tweetcat[2]][tweetcat[1]] + 1
                    Summary["Total"][tweetcat[1]] = Summary["Total"][tweetcat[1]] + 1
    return(Summary)

def TypePieChart(dict):
    Labels = dict.keys()
    Values = [dict[key] for key in dict.keys()]
    plt.pie(Values,None,Labels, autopct='%1.1f%%')

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



def thread_graphing(input_file='data//Thread_Tweet_Structure_at_1563435934.7016308.json'):
    Threads_Forest = nx.DiGraph()

    # Thread_List = list()

    f = open(input_file, 'r')
    Full_data=json.loads(f.readline())
    for reply in Full_data: # Nodes are
        Threads_Forest.add_node(reply[0], user=reply[2])
        Threads_Forest.add_node(reply[1], user=reply[3])
        Threads_Forest.add_edge(reply[0],reply[1], type=reply[4])
    # print(len(Full_data))

    return(Threads_Forest)

# Given the thread forest, we have some things to do...



follower=True #False

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

thread = False # True

if thread == True:
    print("Get Threads Data")
    Thread_Graphs = thread_graphing()
    Undir_Threads = Thread_Graphs.to_undirected()
    Thread_Sets = nx.connected_components(Undir_Threads)
    Size_Hist = [len(c) for c in sorted(Thread_Sets, key=len, reverse=True)]

    # test=Thread_Sets.__next__()

    # I need to classify threads by length and participants
    Thread_Sets = nx.connected_components(Undir_Threads)
    Thread_Forest = [nx.subgraph(Thread_Graphs, subset) for subset in Thread_Sets]
    # The Forest is a list of directed Graphs.

    #For each tree in the forest, I need to find the structure, in terms of users and replies.
    TypeSet= set()
    TreeClassifyGram = {}
    TreeClassifyGram_WithTypes = {}
    for tree in Thread_Forest:
        userset = set()
        type = None
        for node in tree.nodes:
            userset.add(tree.node[node]['user'])
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





    plotting=False

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

