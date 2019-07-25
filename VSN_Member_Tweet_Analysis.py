from Tweet_File_Analysis_Functions import *

def Build_VSN_Filelist():
    # Build list of VSN Member Tweet Files.
    User_Tweet_filelist = Get_FileList_Of_JSON_Files('Data', 'Tweets_by')
    VSN_Member_IDs = [user['id'] for user in
                      GetListFile("data\\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json")]
    VSN_Member_ID_to_Names = {user['id']:user['screen_name'] for user in
                      GetListFile("data\\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json")}
    VSN_Member_Filelist = list()
    VSN_File_to_Names_Map = VSN_Member_ID_to_Names.copy()
    for userID in VSN_Member_IDs:
        Found = False
        for file in User_Tweet_filelist:
            if "Tweets_by_" + str(userID) in file:
                VSN_Member_Filelist.append(file)
                Found = True
                VSN_File_to_Names_Map[file] = VSN_File_to_Names_Map.pop(userID)
        if Found == False:
            print("User", str(userID), "Not Found")
            print("Note: User 988491085642022912 never Tweeted.")
    return(VSN_Member_Filelist, VSN_File_to_Names_Map)


def Build_Type_Graphs(Tweet_Type_Per_File_Dict,File_Name_Map):
    # Calculate Distribution from dict:
    import pandas as pd
    Agg_Type_df = pd.DataFrame(Tweet_Type_Per_File_Dict)
    Agg_Type_df = Agg_Type_df.rename({0:'Monologue', 1:'Reply', 2:'Quote', 3:'Mix'},axis=0)
    Agg_Type_df = Agg_Type_df.rename(File_Name_Map,axis=1)
    Agg_Type_Pct_df = Agg_Type_df.apply(lambda x: x/x.sum(), axis=0)

    import seaborn as sns

    sns.set(style="ticks", palette="pastel")

    data = []
    for row in Agg_Type_Pct_df.iterrows():
        ttype = row[0]
        user = [x for x in row[1].index]
        pct = [x for x in row[1].array]
        for n in range(0,len(row[1])):
            data.append((user[n], ttype, pct[n]))
    flat_df = pd.DataFrame(data, columns=['User', 'Tweet Type', 'Percentage'])

    import matplotlib as plt
    import matplotlib.pylab as pyl
    plt.rc('ytick', labelsize=5.5)
    plt.rc('ytick', labelsize=5.5)

    ax = sns.scatterplot(data=flat_df, x="Percentage", y="User", hue="Tweet Type")
    ax.set_aspect(aspect=0.04)
    pyl.setp(ax.get_legend().get_texts(), fontsize='6') # for legend text
    pyl.setp(ax.get_legend().get_title(), fontsize='8') # for legend title

    pyl.savefig('Tweet Pcts.png')
    return(0)


# Analysis:

VSN_Member_Filelist, VSN_File_to_Names_Map = Build_VSN_Filelist()

Tweet_Counts = Count_Tweets(VSN_Member_Filelist,DateRange=DateRange)
Non_Retweet_Types = Scan_Files_With_Function_Filter(VSN_Member_Filelist, tweet_is_reply, Silent=True,
                                                               DateRange=DateRange)

Build_Type_Graphs(VSN_Member_Filelist, VSN_File_to_Names_Map)

List_VSN_Interaction_Tweets = Scan_Files_With_Function_Filter(VSN_Member_Filelist, tweet_is_reply, Silent=True,
                                                           DateRange=DateRange, AggNotList=False, exclude=[0])


# Dict Mapping File: Username.

def SumAggDict(Dict_List):
    Agg = {}
    for dict in Dict_List:
        for key in Dict_List[dict].keys():
            if key in Agg.keys():
                Agg[key] = Agg[key] + Dict_List[dict][key]
            else:
                Agg[key] = Dict_List[dict][key]
    return(Agg)


# Pretty Histogram-ish thing (Scatterplot, but...)

Pict = False
if Pict:
    Aggregate_VSN_Tweet_Type = Scan_Files_With_Function_Filter(VSN_Member_Filelist, tweet_is_reply, Silent=True,
                                                               DateRange=DateRange)
    Build_Type_Graphs(VSN_Member_Filelist, VSN_File_to_Names_Map)

# Look at Filelist, find...?

FewFiles= VSN_Member_Filelist[3:7]
