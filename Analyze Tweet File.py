# The tweets have been retreived and saved to files. I need to loop through them, and find several features.

# 1. Are they potentially vaccine-relevant based on keywords? (If not, ignore.)

# 2. Which tweets are replies, and to whom (can be multiple ppl involved.)
# 2a. This list will drive further collection to attempt to make sure conversations are captured
# 2b. Flag / compile data structure of everyone in conversations / followed by original list / etc.

# 3. Index all links used.
# 3a. Check if they are journal articles / press articles / fake news sites / etc - potentially hard to do.
# 3b....

import json
import time
from itertools import islice

def GrabFileTweets(Filename, start, end):
    """
    Grab a subset of the Tweets in the file, structured as output by Retreive Data.py
    (This can allow running multiple sections in parallel.)

    Args:
        Filename: File
        start: First line/tweet to get  (inclusive)
        end: Last Tweet to get (inclusive)

    Returns:
        Data Structure (list) of some of the tweets.

    Raises:
        TypeError: If it gets something that it can't parse.
        ValueError: No Tweets Returned
    """

    output = list()

    with open(Filename) as fp:
        for i, line in enumerate(fp):
            if i > end:
                break
            elif i >= start:
                output.append(json.loads(line))
    if len(output)==0:
        output=None
    return(output)



Vaccine_Terms = ['mmr', 'dtap', 'measles', 'mumps', 'rubella', 'diptheria', 'tetanus', 'pertussis', 'whooping cough']
MisInfo_Terms =['autism', 'poison', 'shills', 'pharma', 'mandatory', 'vaers', 'aluminum', 'mercury', 'thimerosal']
HealthEd_Terms = ['vaccine', 'immunocompromise', 'preventable disease', 'rumors', 'debunk', 'expert']
All_Terms = Vaccine_Terms + MisInfo_Terms + HealthEd_Terms

def RelevantTweet(Tweet,Termlist, DateRange=None):
    """
    Return True/False for relevance.

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
    TweetText = Tweet["text"].lower() #ignore case.

    # From: https://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
    if DateRange is not None:
        ts = time.strptime(Tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

        if ts < time.strptime(DateRange[0], '%b %d %H:%M:%S %Y'):
            return False
        elif ts > time.strptime(DateRange[1], '%b %d %H:%M:%S %Y'):
            return False
    if Termlist is not None:
        for word in Termlist:
            if word.lower() in TweetText:
                return True
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
                if RelevantTweet(tweet_item, TermList,DateRange):
                    f.write(json.dumps(tweet_item))
                    f.write('\n')
                    TweetCount=TweetCount+1
    return(TweetCount)

def Get_ReplyList(File, SN=False):
    Replied_To = list()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        tweet_item = json.loads(current_line)
        if tweet_item["in_reply_to_user_id"] is not None:
            if SN:
                Replied_To.append(tweet_item["in_reply_to_screen_name"])
            else:
                Replied_To.append(tweet_item["in_reply_to_user_id"])
    return(Replied_To)


def Get_Reply_TweetID_List(File):
    ID_Replied_To = list()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        tweet_item = json.loads(current_line)
        if tweet_item["in_reply_to_status_id"] is not None:
            ID_Replied_To.append(tweet_item["in_reply_to_status_id"])
    return(ID_Replied_To)


def Get_IDs_From_Users(File):
    IDList = List()
    input_file = open(File, 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:
        return(0) # Unfinished.

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

def AppendToListFile(Input, File, Unique=False): #Given a file that is a list, add another list
    Current_List = list()
    with open(File, 'r') as f:
        Current_List = json.loads(f.readline()) # It only has one line, so...
        f.close()
    orig_len = len(Current_List)

    with open(File, 'w+') as f:
        if Unique:
            f.write(json.dumps(list(set(Current_List + Input))))
        else:
            f.write(json.dumps(Current_List + Input))
        f.close()
    print("Appended ", len(Input), "Items to the original ", orig_len)


def Get_FileList_Of_JSON_Files(directory):
    import os
    JSONfileList = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                JSONfileList.append(directory + '/' + file)
    return JSONfileList


if __name__ == "__main__":
    flist = ["tweet_data_Partial1.json","tweet_data_Partial2.json", "tweet_data_Partial3.json",
             "tweet_data_Partial4.json", "tweet_data_Partial5.json"]
    DateRange=["Jan 01 00:00:00 2018","Jan 01 00:00:00 2019"] #Sent during 2018.
    OutFile = 'relevant_tweets.json'
    #   count=Pull_Relevant(flist, DateRange, All_Terms, OutFile)
    #   print(count) # Output: 21229 #All tweets from original list members.

    # Get the Tweet IDs
    #ListRepliesIDs(TweetFile, ID_List_Outfile)

    #Pull Relevant from Replies (Not the actual replies, the tweets that are independently "Relevant")
    # TweetFile = 'relevant_tweets.json'
    # WriteReplyListIDs(TweetFile, "Initial_Replied_IDList.json")
    genflist = Get_FileList_Of_JSON_Files(r'Data')
    #print(genflist)
    #OutFile = 'Data\All_Replies_Relevant_Scan.json'
    #ReplyListcount = Pull_Relevant(genflist, DateRange, All_Terms, OutFile)

    #Check that list file stuff Works:
    #WriteNewList(['a','b','c'], "test.json")
    #AppendToListFile(['b', 'c', 'd'], "test.json")
    #AppendToListFile(['b','c','d'], "test.json", Unique=True)
    # All Good.

    #Get_Tweets_By_IDList(Tweet_ID_List, genflist, OutFile)

    #WriteNewList(ListAllTweetIDs('relevant_tweets.json'), 'Initial_Relevant_Tweet_ID_List.json')

    #WriteNewList(Get_Reply_TweetID_List('relevant_tweets.json'), "Reply_IDs_From_relevant_tweets.json")

    Get_Tweets_By_IDList(Get_Reply_TweetID_List('relevant_tweets.json'),
                         genflist, "Tweets_Replied_To_By_Initial_List.json")

    #WriteNewList(ListAllTweetIDs('Data/All_Replies_Relevant_Scan.json'), 'Replies_Relevant_Tweet_Scanned_ID_List.json')


