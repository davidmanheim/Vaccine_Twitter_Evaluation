
import json
import time
from itertools import islice

DateRange = ["Jan 01 00:00:00 2018", "Jan 01 00:00:00 2019"] #Sent during 2018.

Vaccine_Terms = ['mmr', 'measles', 'mumps', 'rubella']
MisInfo_Terms = ['autism', 'poison', 'shills', 'pharma', 'mandatory', 'vaers', 'aluminum', 'mercury', 'thimerosal']
HealthEd_Terms = ['vaccine', 'immunocompromise', 'preventable disease', 'rumors', 'debunk', 'expert',
                  "infectious disease", "immunization"]
All_Terms = Vaccine_Terms + MisInfo_Terms + HealthEd_Terms


def RelevantTweet(Tweet, Termlist, DateRange=None):
    """
    Return True/False for relevance.

    (Include quoted tweets in scan.)

    Args:
        Tweet: Full tweet structure
        Termlist: List structure of items that would make tweet relevant
        DateRange: None, or dates [Begin,End] for when the tweet needs to have been sent.
        Format is '%b %d %H:%M:%S %Y')

    Returns:
        True/False

    Raises:
        TypeError: If it gets a tweet not formatted how it expects.
    """
    TweetText = Tweet["full_text"].lower() #ignore case. # Changed to full_text now, instead of (previously) truncated.

    if Tweet["is_quote_status"] is True: #Append, since we're just matching terms.
        # print("Tweet = ", Tweet.keys())
        if "quoted_status" in Tweet:
            TweetText = TweetText + " " + Tweet["quoted_status"]["full_text"].lower()

    # From: https://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
    if DateRange is not None:
        ts = time.strptime(Tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

        if ts < time.strptime(DateRange[0], '%b %d %H:%M:%S %Y'):
            return False
        elif ts > time.strptime(DateRange[1], '%b %d %H:%M:%S %Y'):
            return False
    if Termlist is None:
        return True
    else:
        for word in Termlist:
            if word.lower() in TweetText:
                return True
        return False

def TweetByUser(Tweet, Userlist, DateRange=None):
    """
    Return True/False for if the tweet is by one of the supplied ids.

    Args:
        Tweet: Full tweet structure
        Userlist: Users to check against
        DateRange: None, or dates [Begin,End] for when the tweet needs to have been sent.
        Format is '%b %d %H:%M:%S %Y')

    Returns:
        True/False

    Raises:
        TypeError: If it gets a tweet not formatted how it expects.
    """
    if Tweet['user']['id'] in Userlist:
        # From: https://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
        if DateRange is not None:
            ts = time.strptime(Tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

            if ts < time.strptime(DateRange[0], '%b %d %H:%M:%S %Y'):
                return False
            elif ts > time.strptime(DateRange[1], '%b %d %H:%M:%S %Y'):
                return False
        return True
    else:
        return False


def Pull_Relevant(flist, DateRange, TermList, OutFile):
    """
    Write relevant tweets from files to a new file. Prints filenames as each is reached, return count of relevant tweets

    Args:
        flist: list of files to pull from
        DateRange: None, or dates [Begin,End] for when the tweet needs to have been sent. Format is '%b %d %H:%M:%S %Y')
        Termlist: List structure of items that would make tweet relevant
        OutFile: Filename to write to. (Appends, does not overwrite!)

    Returns:
        integer
    """

    TweetCount=0
    for Filename in flist:
        Tweetset_Current = "Start"
        print(Filename)
        input_file = open(Filename, 'r')
        raw_batch = islice(input_file, None)
        with open(OutFile, 'a') as f: # append the batch, and close file each time.
            for current_line in raw_batch:
                tweet_item = json.loads(current_line)
                if RelevantTweet(tweet_item, TermList, DateRange):
                    f.write(json.dumps(tweet_item))
                    f.write('\n')
                    TweetCount=TweetCount+1
    return(TweetCount)

def Get_ReplyList(File, SN=False):
    """
    Get list of reply / quoted tweets user IDs

    Args:
        File: Files to pull from
        SN: If screen names are used in place of IDs (Don't do this - it's a bad idea)

    Returns:
        list of users whose tweets were replied to / quoted / quoted tweet replies in the tweet
    """
    if SN:
        raise NotImplementedError
    Replied_To = list()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        tweet_item = json.loads(current_line)
        if tweet_item["in_reply_to_user_id"] is not None:
            Replied_To.append(tweet_item["in_reply_to_user_id"])
        if tweet_item["is_quote_status"]:
            if "quoted_status" in tweet_item:
                Replied_To.append(tweet_item["quoted_status"]['user']['id'])
                if tweet_item["quoted_status"]["in_reply_to_user_id"] is not None:
                    Replied_To.append(tweet_item["quoted_status"]["in_reply_to_user_id"])
    return(Replied_To)

def Get_MentionList(File, SN=False):
    Mentioned = list()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        tweet_item = json.loads(current_line)
        if tweet_item["user_mentions"] is not None:
            if SN:
                raise NotImplementedError
            else:
                for user in tweet_item["user_mentions"]:
                    Mentioned.append(user["id"])
    return(Mentioned)

def Get_Reply_TweetID_List(File):
    ID_Replied_To = list()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        tweet_item = json.loads(current_line)
        if tweet_item["in_reply_to_status_id"] is not None:
            ID_Replied_To.append(tweet_item["in_reply_to_status_id"])
        if tweet_item["is_quote_status"]:
            if "quoted_status" in tweet_item:
                if tweet_item["quoted_status"]["in_reply_to_user_id"] is not None:
                    ID_Replied_To.append(tweet_item["quoted_status"]["in_reply_to_status_id"])
    return(ID_Replied_To)


def Get_IDs_From_Users(File):
    IDList = List()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        raise NotImplementedError('Don\'t use Get_IDs_From_Users.')
        # return 0 # Unfinished.

def ListRepliesIDs(TweetFile, ID_List_Outfile): #List all Tweet IDS that are replies.
    Reply_ids = Get_ReplyList(TweetFile, SN=False)
    with open(ID_List_Outfile, 'w+') as f:
        f.write(json.dumps(Reply_ids))
    from collections import Counter
    return len(Counter(Reply_ids).keys())

def ListAllTweetIDs(TweetFile): #List all Tweet IDs that are in a given file.
    ID_List=list()
    with open(TweetFile, 'r') as f:
        Contents = islice(f, None)
        for line in Contents:
            #print(line)
            tweet = json.loads(line)
            ID_List.append(tweet["id"])
    return(ID_List)

def Get_Tweets_By_IDList(Tweet_ID_List, Infile_List, OutFile):
    TweetCount=0
    for Filename in Infile_List:
        input_file = open(Filename, 'r')
        raw_batch = islice(input_file, None)
        with open(OutFile, 'a') as f: # append the batch, and close file each time.
            for current_line in raw_batch:
                tweet_item = json.loads(current_line)
                if tweet_item['id'] in Tweet_ID_List:
                    f.write(json.dumps(tweet_item))
                    f.write('\n')
                    TweetCount=TweetCount+1
    return(TweetCount)

def WriteNewList(Input, File): # Removes anything already there!
    with open(File, 'w+') as f:
        f.write(json.dumps(Input))

def GetListFile(File):  # Given a file that is a list, get items
    f = open(File, 'r')
    List_from_file = list()
    for line in f:
        List_from_file = json.loads(line)
    f.close()
    return(List_from_file)


def AppendToListFile(Input, File, Unique=False): #Given a file that is a list, add another list
    with open(File, 'r') as f:
        Current_List = json.loads(f.readline()) # It only has one line, so...
        f.close()
    orig_len = len(Current_List)

    with open(File, 'w+') as f:
        if isinstance(Input, list):
            Current_List.extend(Input)
            if Unique:
                f.write(json.dumps(list(set(Current_List))))
            else:
                f.write(json.dumps(Current_List))
        else:
            if Unique:
                if Input not in Current_List:
                    Current_List.append(Input)
            else:
                Current_List.append(Input)
            f.write(json.dumps(Current_List))
        f.close()
    print("Appended ", len(Input), "Items to the original ", orig_len)


def Get_FileList_Of_JSON_Files(directory, prefix=None, suffix='.json', contains=None):
    import os
    JSONfileList = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix):
                if prefix is not None:
                    if file.startswith(prefix):
                        if contains is not None:
                            if contains in file:
                                JSONfileList.append(directory + '/' + file)
                        else:
                            JSONfileList.append(directory + '/' + file)
                else:
                    JSONfileList.append(directory + '/' + file)
    return JSONfileList

# def Scan_Files_With_Function_Filter(Filelist, Filter, AggNotList=True, Silent=True, **kwargs):
#     # This will return a dict per-file for what the filter returns aggregated over the items in each file.
#     # (Intended to use on lists of files containing 1-tweet-per-line.)
#     Aggregate_Dict = {}
#     for File in Filelist:
#         if not Silent:
#             print("Now processing file", File)
#         if AggNotList:
#             File_Out = {}
#         else:
#             File_Out = []
#         with open(File, 'r') as f:
#             Contents = islice(f, None)
#             for line in Contents:
#                 item = json.loads(line)
#                 answer = Filter(item, **kwargs)
#                 if AggNotList:
#                     if answer in File_Out.keys():
#                         File_Out[answer] = File_Out[answer] + 1
#                     else:
#                         File_Out[answer] = 1
#                 else:
#                     File_Out.append(answer)
#             Aggregate_Dict[File] = File_Out.copy()
#     return(Aggregate_Dict)

def Scan_Files_With_Function_Filter(Filelist, Filter, AggNotList=True, Silent=True, Exclude=None, **kwargs):
    # IMPORTANT NOTE: if Exclude is set to anything, it will ALSO exclude Answer == None.
    # Otherwise, it will be included.
    # This will return a dict per-file for what the filter returns aggregated over the items in each file.
    # (Intended to use on lists of files containing 1-tweet-per-line.)
    # If List, instead of Agg, it will contain a list of the IDs per category instead of a count
    Aggregate_Dict = {}
    for File in Filelist:
        if not Silent:
            print("Now processing file", File)
        File_Out = {}
        with open(File, 'r') as f:
            Contents = islice(f, None)
            if Contents is not None:
                for line in Contents:
                    # print(line)
                    if line is not None:
                        item = json.loads(line)
                        answer = Filter(item, **kwargs)
                        if answer is not None:
                            if Exclude is not None:
                                if answer in Exclude:
                                    ExcludeMe = True
                                else:
                                    ExcludeMe = False
                            else:
                                ExcludeMe = False
                        elif None in Exclude: #Answer is None, so we check - does it get excluded?
                                ExcludeMe = True
                        else:
                            ExcludeMe = False
                        #Now, check if it is excluded, then add it to the list
                        if not ExcludeMe:
                            if AggNotList:
                                if answer in File_Out.keys():
                                    File_Out[answer] = File_Out[answer] + 1
                                else:
                                    File_Out[answer] = 1
                            else:
                                if answer in File_Out.keys():
                                    File_Out[answer].append(item["id"])
                                else:
                                    File_Out[answer] = [item["id"]]
            Aggregate_Dict[File] = File_Out.copy()
    return(Aggregate_Dict)

def Count_Tweets(Filelist, DateRange=None):
    def CountTweet(tweet):
        if DateRange is not None:
            ts = time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if ts < time.strptime(DateRange[0], '%b %d %H:%M:%S %Y'):
                return("OOR")
            elif ts > time.strptime(DateRange[1], '%b %d %H:%M:%S %Y'):
                return("OOR")
            if "retweeted_status" in tweet.keys():
                return("Retweets")
            else:
                return("Tweets")
        else:
            if "retweeted_status" in tweet.keys():
                return("Retweets")
            else:
                return("Tweets")
    Tweet_Counts = Scan_Files_With_Function_Filter(Filelist,CountTweet)
    Tweets = 0
    RTs = 0
    for user in Tweet_Counts:
        if "Tweets" in Tweet_Counts[user].keys():
            Tweets = Tweets + Tweet_Counts[user]["Tweets"]
        if "Retweets" in Tweet_Counts[user].keys():
            RTs = RTs + Tweet_Counts[user]["Retweets"]
    return({"Non-RT_Total": Tweets, "RT_Total": RTs})

def Tweet_Type_Filter(tweet, **kwargs):
    if type(tweet) == "dict":
        return(0)
    else:
        return(1)

def Scan_Files_For_Thread_Items(TweetIDlist, Filelist, OutFile,IncludeQuoteOrReply=True):
    if not isinstance(TweetIDlist, list): #Assume it's a filename.
        TweetIDlist=GetListFile(TweetIDlist)

    TweetCount=0

    with open(OutFile, 'w+') as f:
        for file in Filelist:
            print("File:", file)
            input_file = open(file, 'r')
            raw_batch = islice(input_file, None)
            for current_line in raw_batch:
                tweet_item = json.loads(current_line)
                if tweet_item['id'] in TweetIDlist:
                    f.write(json.dumps(tweet_item))
                    f.write('\n')
                    TweetCount = TweetCount + 1
                elif IncludeQuoteOrReply:
                    if tweet_item["in_reply_to_status_id"] is not None:
                        if tweet_item["in_reply_to_status_id"] in TweetIDlist:
                            f.write(json.dumps(tweet_item))
                            f.write('\n')
                            TweetCount = TweetCount + 1
                    elif "quoted_status_id" in tweet_item:
                        if tweet_item["quoted_status_id"] in TweetIDlist:
                            f.write(json.dumps(tweet_item))
                            f.write('\n')
                            TweetCount = TweetCount + 1
    return(TweetCount)

def tweet_is_reply(tweet, DateRange=None, Exclude_RTs=True, **kwargs):
    output = 0
    if Exclude_RTs:
        if "retweeted_status" in tweet.keys():
            return(None)
    if tweet["in_reply_to_status_id"] is not None:
        output = output + 1
    if "quoted_status_id" in tweet:
        output = output + 2
    if DateRange is not None:
        ts = time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if ts < time.strptime(DateRange[0], '%b %d %H:%M:%S %Y'):
            pass
        elif ts > time.strptime(DateRange[1], '%b %d %H:%M:%S %Y'):
            pass
        else:
            return (output)
    else:
        return(output)


def get_followers(api=None, screen_name=None):
    users = api.GetFollowerIDs(screen_name=screen_name)  # Should be using User IDs. Fixed.
    return users

def Get_UserIds_From_UserList_File(File):
    Out_list = []
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:  # Per Tweet.
        user_item = json.loads(current_line)
        Out_list.append(user_item['id'])


def Get_Users_From_Tweet_Files(Filelist, Outfile, UserIDList=None, ExcludeUserIDList=None):

    if isinstance(ExcludeUserIDList,list):
        Exclude_Users = ExcludeUserIDList.copy()
    elif isinstance(ExcludeUserIDList,str):
        Exclude_Users = GetListFile(ExcludeUserIDList)
    else:
        Exclude_Users = []

    def add_user(user_item, outfile):
        userid = user_item['id']
        if userid not in Exclude_Users:
            if UserIDList is not None:
                if userid not in UserIDList:
                    return 0
            outfile.write(json.dumps(userid))
            outfile.write('\n')
            Exclude_Users.append(userid)
            return 1
        return 0

    count = 0

    with open(Outfile, 'w+') as f:
        for file in Filelist:
            print("File:", file)
            input_file = open(file, 'r')
            raw_batch = islice(input_file, None)
            for current_line in raw_batch: # Per Tweet.
                tweet_item = json.loads(current_line)
                user_item = tweet_item["user"]
                count = count + add_user(user_item,f)
    return(count)

def Classify_User(Filelist, Classes): #Classes is a dict with an entry for (if ints) a userid list,
    # or (if str) a term list.
    # Example: Classes={"VSN_Member":[1,2,3,], "Doctor": ["dr.", "doctor"], "OrgTerm": ["National", "Official"]}

    # Output is a dict per userid with: "username", "description", "verified", and one entry per class which is True / False
    Output = {}

    if isinstance(Filelist, str): # Only 1 file.
        Filelist = [Filelist]

    for file in Filelist:
        print("File:", file)
        input_file = open(file, 'r')
        raw_batch = islice(input_file, None)
        for current_line in raw_batch:  # Per User.
            user_item = json.loads(current_line)
            Output[user_item["id"]] = {"username": user_item["name"], "description": user_item["description"],
                                       "verified": user_item["verified"]}
            if "entities" in user_item.keys():
                if "url" in user_item["entities"].keys():
                    Output[user_item["id"]]["Website"] = user_item["entities"]["url"]["urls"][0]["expanded_url"]
            for This_Class in Classes:
                if isinstance(Classes[This_Class][0], int):
                    if user_item["id"] in Classes[This_Class]:
                        Output[user_item["id"]][This_Class] = True
                    else:
                        Output[user_item["id"]][This_Class] = False
                elif isinstance(Classes[This_Class][0], str):
                    Output[user_item["id"]][This_Class] = \
                        any(term.lower() in user_item["description"].lower() for term in Classes[This_Class])
        return(Output)

def Classify_UserItem(user_item, Classes):
    Output = {}
    Output[user_item["id"]] = {"username": user_item["name"], "description": user_item["description"],
                               "verified": user_item["verified"]}
    if "entities" in user_item.keys():
        if "url" in user_item["entities"].keys():
            Output[user_item["id"]]["Website"] = user_item["entities"]["url"]["urls"][0]["expanded_url"]
    for This_Class in Classes:
        if isinstance(Classes[This_Class][0], int):
            if user_item["id"] in Classes[This_Class]:
                Output[user_item["id"]][This_Class] = True
            else:
                Output[user_item["id"]][This_Class] = False
        elif isinstance(Classes[This_Class][0], str):
            Output[user_item["id"]][This_Class] = \
                any(term.lower() in user_item["description"].lower() for term in Classes[This_Class])
    return(Output)

def Get_User_Classification_Data():
    import os as os
    # Data was pulled / analyzed in User_Extraction_And_Analysis.py
    if os.path.isfile('data\Classified_Users_One_line.json'):  # I haven't pulled the data yet.
        if os.path.isfile("data\Classified_Users_With_Wikimedia_One_line.json"):  # I haven't pulled the data yet.
            with open("data\Classified_Users_With_Wikimedia_One_line.json", 'r') as r:
                Users_Classified = json.loads(r.readline())
    return Users_Classified

def Missing_Tweets_from_Thread_File(TweetIDlist,ThreadFile):
    # TODO: Write this.
    return 0