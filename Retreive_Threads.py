__author__ = 'dmanheim'

import time
import twitter
import json
from itertools import islice
from PrivateKeys import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET

api = twitter.Api(
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True, tweet_mode='extended'
)

# First, we need to find tweets that are replies or quote tweets.

from Tweet_File_Analysis_Functions import Get_FileList_Of_JSON_Files, AppendToListFile, GetListFile

# Scan_Files_For_Thread_Items(TweetIDlist, Filelist)
# This scans a file, or list of files, for Replies and Quote-Tweets that are in the list of IDs.

def Scan_Files_For_Replies(Filelist, OutFile): # Outfile has a list of tweet IDs that were replied to/quoted, to find.
    if not isinstance(Filelist, list): #Assume it's a filename.
        Filelist=[Filelist]

    TweetCount=0

    List_to_Add = list() # List of tuples, containing:
    # Original Tweet ID, ReplyID, Original User ID, Reply to User ID, Type)

    for file in Filelist:
        Sublist=list()
        print("Scanning File:", file)
        input_file = open(file, 'r')
        raw_batch = islice(input_file, None)
        for current_line in raw_batch:
            tweet_item = json.loads(current_line)
            if tweet_item["in_reply_to_status_id"] is not None:
                new_tuple = (tweet_item["id"], tweet_item["in_reply_to_status_id"],
                             tweet_item["user"]["id"], tweet_item["in_reply_to_user_id"], "Reply")
                if tweet_item["is_quote_status"]:
                    # print(tweet_item["full_text"][0:2])
                    # print(tweet_item.keys())
                    if "quoted_status" in tweet_item.keys():
                        # print(tweet_item["user"]["screen_name"], tweet_item["id"])
                        new_tuple = (tweet_item["id"], tweet_item["quoted_status_id"],
                                     tweet_item["user"]["id"], tweet_item["quoted_status"]["user"]["id"], "Quote")
                        Sublist.append(new_tuple)
                Sublist.append(new_tuple)
            elif tweet_item["is_quote_status"]:
                # print(tweet_item["full_text"][0:2])
                # print(tweet_item.keys())
                if "quoted_status" in tweet_item.keys():
                    # print(tweet_item["user"]["screen_name"], tweet_item["id"])
                    new_tuple = (tweet_item["id"], tweet_item["quoted_status_id"],
                                tweet_item["user"]["id"], tweet_item["quoted_status"]["user"]["id"], "Quote")
                    Sublist.append(new_tuple)
        List_to_Add.extend(Sublist)
        with open(Outfile, 'w+') as f:
            f.write(json.dumps(List_to_Add))
            f.close()
    return(len(List_to_Add))

def get_tweets_by_IDs(api=None, ID_List=None, Outfile="tests.json"):
    retrieved = api.GetStatuses(ID_List)
    print("Get Successful...")
    with open(Outfile, 'a') as f:
        for tweet in retrieved:
            f.write(json.dumps(tweet._json))
            f.write('\n')
    return(len(retrieved))



if __name__ == "__main__":
    # Outfile = "Data\Thread_Tweet_Structure_at_" + str(time.time()) + ".json"
    # All_data_files = Get_FileList_Of_JSON_Files("data", "Tweets_by")
    # with open(Outfile, 'w+') as f:
    #     f.close()

    # Scan_Files_For_Replies(All_data_files, Outfile)

    # After the above was done, We try to retrieve those other tweets. First, build a list:
    Tweet_Structure_files = Get_FileList_Of_JSON_Files("data", "Thread_Tweet_Structure")
    ListofReplyStruct = list()
    Tweet_Structure_files.sort()
    ListofReplyStruct.extend(GetListFile(Tweet_Structure_files[-1])) # Because the most recent one has everything.

    # Each entry has: (Original Tweet ID, ReplyID, Original User ID, Reply to User ID, Type)
    print("Extract what to retrieve from file")
    List_to_get = list()
    for entry in ListofReplyStruct:
        List_to_get.append(entry[1]) # Item 1 is the IF of the tweet replied to / embedded.

    # This is too big. Let's get 5k/time. (100 per request * 50 requests - limit at 300 requests / 15 minutes)
    Running_list_File = 'Thread_Tweets_Retrieved.json'
    # Create that file: f = open('Thread_Tweets_Retrieved.json', 'w+'); f.write(json.dumps([])); f.close()
    Outfile = 'data\\tweets_By_ID_at_' + str(time.time()) + '.json'

    from numpy import setdiff1d
    Dontget = GetListFile(Running_list_File) #This broke before. Rebuilding is below.

    # Rebuild Dontget from actual retrieved data:
    # f = open('Thread_Tweets_Retrieved.json', 'w+'); f.write(json.dumps([])); f.close()
    # Dontget= list()
    # All_reply_data_files = Get_FileList_Of_JSON_Files("data", "tweets_By_ID_at")
    # for file in All_reply_data_files:
    #     print("checking file:", file)
    #     MoreTweets = list()
    #     with open(file, 'r') as f:
    #         raw_batch = islice(f, None)
    #         for current_line in raw_batch:
    #             tweet_item = json.loads(current_line)
    #             MoreTweets.append(tweet_item["id"])
    #     AppendToListFile(MoreTweets,'Thread_Tweets_Retrieved.json')
    #     Dontget.extend(MoreTweets)

    Still_Needed = setdiff1d(List_to_get, Dontget)
    print("There are", len(Dontget), "identified tweets to retreive, all but ", len(Still_Needed), "are already pulled",
          "with a total set of", len(List_to_get), "tweet reply items so far.")

    Chunks = [Still_Needed[x: x+5000] for x in range(0, len(Still_Needed), 5000)] # Get Chunks.
    #That's a numpy data type. Bad. int above to allow jsonify, fix zip below to make list not tuple.
    # print(Chunks[0])
    for chunk in Chunks:
        print("Get another", len(chunk), "items")
        get_tweets_by_IDs(api, chunk, Outfile)
        AppendToListFile([int(id) for id in chunk], Running_list_File)
        print("Chunk Retrieved and written")

    print("Retrieval finished. Now getting new structures from retrieved data")

    All_reply_data_files = Get_FileList_Of_JSON_Files("data", "tweets_By_ID_at")
    Outfile = "Data\Thread_Tweet_Structure_at_" + str(time.time()) + ".json"
    with open(Outfile, 'w+') as f:
        f.close()
    All_reply_data_files.sort()

    # Marginal data only:
    #new_tweets_to_get = Scan_Files_For_Replies(All_reply_data_files[-1:], Outfile)
    # Struct with everything:
    new_tweets_to_get = Scan_Files_For_Replies(All_reply_data_files, Outfile)

    print("File(s) scanned, and", new_tweets_to_get, "new tweets reply structs are now in:", Outfile)

    #Just keep re-running. Looping would be better, but it's not worth re-doing now.
    # The tail is longer than expected. If I weren't stupidly stubborn I'd code a loop now.
    # Looks like there are at least 30 with chains of 100 tweets or more...
    # And probably 10 that are 200...
    # I'm only somewhat reassured by the understanding that all chains must terminate.
    # Stopping for now, with only 5 threads still going - at least a few of which are clearly trolls.