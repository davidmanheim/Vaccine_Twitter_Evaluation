__author__ = 'dmanheim'

import os
import twitter
import time
# import oauth2 as oauth
import time
import json
from PrivateKeys import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET

# Key Files used:
# Updating_Pulled_Exclude_IDs.json - This file contains IDs of users whose tweets were already retrieved.
# Create:         f = open("Updating_Pulled_Exclude_IDs.json", 'w+'); f.write(json.dumps([])); f.close()
# Users_To_Retrieve.json - This is where we append (additional) users whose data we want to retrieve.
# Create:         f = open("Users_To_Retrieve.json", 'w+'); f.write(json.dumps([])); f.close()

# Updating_Scanned_Userfile_List.json - This is a list of files already checked for relevant tweets.
# Create:         f = open("Updating_Scanned_Userfile_List.json", 'w+'); f.write(json.dumps([])); f.close()

# "Thread_Tweet_IDList.json" - This is the IDs of tweets that were replied to by relevant tweets,
# which may not themselves be relevant
# Create:         f = open("Thread_Tweet_IDList.json", 'w+'); f.write(json.dumps([])); f.close()

def add_list_to_retreive(api=None,user=None,list_slug=None):
    # print(screen_name)
    List_Members = api.GetListMembers(slug=list_slug, owner_screen_name=user) #Formatted as list of users
    List_Members_List = []
    for Member in List_Members:
        List_Members_List.append(Member.AsDict())
    with open("data//List_"+list_slug +"_By_"+user+"_at_"+str(time.time())+".json", 'w+') as f:
        f.write(json.dumps(List_Members_List))  # Keep the Data

    Excluded_file = open("Updating_Pulled_Exclude_IDs.json", 'r')
    ToGet_file = open("Users_To_Retrieve.json", 'r')
    for line in Excluded_file:
        excludeIDs = json.loads(line)
    Excluded_file.close()
    for line in ToGet_file:
        ToGetIDs = json.loads(line)
    ToGet_file.close()
    for member in List_Members:
        id = member.AsDict()['id']
        if id not in excludeIDs:
            if id not in ToGetIDs:
                ToGetIDs.append(id)
    with open("Users_To_Retrieve.json", 'w+') as f:
        f.write(json.dumps(ToGetIDs))  # Replace old list with new one.


# This function retrieves tweets from users since a given year
def get_tweets(api=None, Userid=None, Earliest_Year=2018):
    try:
        timeline = api.GetUserTimeline(user_id=Userid, count=200, include_rts=1)
    except twitter.error.TwitterError as TE:
        print("Error for user: ", Userid)
        if TE.message == "Not authorized.":
            print("Not authorized, next.")
            return 0
        elif TE[0]['code'] == 88:
            print('sleeping of 15 minutes')
            time.sleep(60*15)
            pass
        return 0
    try:
        earliest_tweet = min(timeline, key=lambda x: x.id).id
    except ValueError:
        print('No earliest Tweet for user')
        return 0
    #Find date of last tweet.
    Last_Time = timeline[-1].AsDict()['created_at']
    Year = int(Last_Time[-4:])

    print("getting tweets starting Tweet #", earliest_tweet, " in ", Year, " for user: ", Userid)
    #This is a string. The last 4 digits are the year, so...
    while Year >= Earliest_Year:
        try:
            # Check if we are already before out search period...
            tweets = api.GetUserTimeline(
                user_id=Userid, max_id=earliest_tweet, count=200, include_rts=1
            )
            Last_Time = tweets[-1].AsDict()['created_at']
            Year = int(Last_Time[-4:])
        except twitter.error.TwitterError as TE:
            print("Error for user: ", Userid)
            if TE.hasattr("message"):
                if TE.message == "Not authorized.":
                    print("Not authorized, next.")
                    return 0
            elif TE['code'] == 88:
                print('sleeping for 15 minutes')
                time.sleep(60 * 15)
                pass
            return 0
        except IndexError as I:
            Year = 1800
            pass
        try:
            new_earliest = min(tweets, key=lambda x: x.id).id
        except ValueError:
            print('No more earliest Tweet for user')
            break
        if not tweets or new_earliest == earliest_tweet:
            break
        else:
            earliest_tweet = new_earliest
            print("getting more tweets before:", earliest_tweet, " in ", Year, " for user: ", Userid)
            timeline += tweets
    return timeline


def run_initial():
    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True,tweet_mode='extended'
    )

    add_list_to_retreive(api, "WHO_VSN", "vsn-members-on-twitter")

    #Other Lists, for future:
    # "vaccine-facts" by @aboutpediatrics "Get the facts about vaccines from these vaccine advocates on twitter."
    # "immunizationorganizations" by ImmunizeClarkCo (a WHO_VSN member.)


    # Compile full list of users to fetch:

    # Write Users already Fetched to persistent file:

# I will need to find replies to and quotes of any tweet in that set in the given time frame. (For that I need IDs.)


# This dataset includes tweets before & after our intended timeline. It needs to be filtered.


# These are now in a file, and it uses IDs, not screen names.
#     Replied_To = []

def get_and_keep_user_tweets(api=None, UserID=None, Earliest_Year=2018):
    timeline = get_tweets(api, UserID, Earliest_Year)
    if timeline == 0:
        print("Skipping this, excluding user.")
    else:
        OutFile = "Data\Tweets_by_" + str(UserID) + "_back_to_" + str(Earliest_Year) + "_at_" + str(time.time()) + ".json"
        with open(OutFile, 'a') as f:
            for tweet in timeline:
                f.write(json.dumps(tweet._json))
                f.write('\n')
                # Get Rate data and sleep if we're too close.
                # time.sleep(15) #Wait a quarter minute per user so that the rate limit isn't hit.
                # This is a ridiculous hack. Fixed by changing the API interface to sleep on hitting rate limit
    return(UserID)


def get_tweets_by_IDs(api=None, ID_List=None):
    retrieved = api.GetStatuses(ID_List)
    print("Get Successful...")
    with open('tweets_By_ID_at_' + str(time.time()) + '.json', 'w+') as f:
        for tweet in retrieved:
            f.write(json.dumps(tweet._json))
            f.write('\n')
    return(0)


def get_tweetlist_from_tabbed_file(filename):
    import csv
    ID_List = []
    with open(filename, newline='') as Tweets_plus_csv:
        reader = csv.reader(Tweets_plus_csv, delimiter='\t')
        next(reader, None)
        for tweet in reader:
            ID_List.append(tweet[0])
    return(ID_List)

# Get from file: "2018_ajph_weaponized_health_10k_data.txt"
# Command run: get_tweets_by_IDs(api,get_tweetlist_from_tabbed_file("2018_ajph_weaponized_health_10k_data.txt"))


#Get Replies

def get_Users_Tweets(api):
    # I need to fetch data for all users in Replied_To
    # It contains duplicates, and may have users whose data was already retrieved.
    Excluded_file = open("Updating_Pulled_Exclude_IDs.json", 'r')
    for line in Excluded_file:
        excludeIDs = json.loads(line)
    Excluded_file.close()
    Get_file = open("Users_To_Retrieve.json", "r")
    for line in Get_file:
        Get_ID = json.loads(line)
    Get_file.close()

    # print("GetID: ", Get_ID)
    for userID in Get_ID:
        # print("userID: ", userID)
        # Need to check if protected!
        # Also, crashes when user has never tweeted, i.e. Feli56686027 - I now check for that.
        # Also, it crashes anyways and I'm doing this in multiple steps / files.
        if userID not in excludeIDs:
            return_ID = get_and_keep_user_tweets(api, userID)
            excludeIDs.append(return_ID)

        with open("Updating_Pulled_Exclude_IDs.json", 'w+') as f:
            f.write(json.dumps(excludeIDs)) #Replace old list with new one. If there is a crash, this helps!

if __name__ == "__main__":
#This uses the file lists to drive what to get, and updates those lists. YAY!

    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True, tweet_mode='extended'
    )

    print("Retrieving users' timelines")
    get_Users_Tweets(api) #If all have been retrieved, it just ends.

    print("Retrieving Relevant tweets")
    from Tweet_File_Analysis_Functions import Get_FileList_Of_JSON_Files, AppendToListFile, GetListFile

    User_Tweet_filelist = Get_FileList_Of_JSON_Files('Data', 'Tweets_by')
    Scanned_File_List = GetListFile("Updating_Scanned_Userfile_List.json")

    # Now, pull the relevant tweets from those created files:
    OutFile = "Data\Relevant_User_Tweets_Scanned_at_" + str(time.time()) + ".json"

    To_Scan_File_List = [File for File in User_Tweet_filelist if File not in Scanned_File_List]

    from Tweet_File_Analysis_Functions import All_Terms, DateRange, Pull_Relevant
    Pull_Relevant(To_Scan_File_List, DateRange, All_Terms, OutFile)
    print("Adding scanned files to exclusion list.")
    AppendToListFile(To_Scan_File_List, "Updating_Scanned_Userfile_List.json", Unique=True)

    print("Get Interacting User List")
    # Now, get users that interacted, and the Tweet IDs of tweets in threads.
    User_Tweet_filelist = Get_FileList_Of_JSON_Files('Data', 'Relevant_User_Tweets')
    from Tweet_File_Analysis_Functions import Get_ReplyList, Get_Reply_TweetID_List
    for file in User_Tweet_filelist:
        IDs_To_add = Get_ReplyList(file)
        Reply_Tweet_IDs = Get_Reply_TweetID_List(file)
        print("Users")
        AppendToListFile(IDs_To_add, "Users_To_Retrieve.json", Unique=True)
        print("TweetIDs")
        AppendToListFile(Reply_Tweet_IDs, "Thread_Tweet_IDList.json")

    print("The script does not yet check if tweets are replies to relevant tweets")

    print("Retrieving users' who replied full timelines")
    get_Users_Tweets(api)  # If all have been retrieved, it just ends.

    print("Retrieving Relevant tweets")
    User_Tweet_filelist = Get_FileList_Of_JSON_Files('Data', 'Tweets_by')
    Scanned_File_List = GetListFile("Updating_Scanned_Userfile_List.json")

    # Now, pull the relevant tweets from those created files:
    OutFile_2 = "Data\Relevant_2nd_Degree_User_Tweets_Scanned_at_" + str(time.time()) + ".json"

    To_Scan_File_List_2 = [File for File in User_Tweet_filelist if File not in Scanned_File_List]

    Pull_Relevant(To_Scan_File_List_2, DateRange, All_Terms, OutFile_2)
    print("Adding 2nd degree scanned files to exclusion list.")
    AppendToListFile(To_Scan_File_List, "Updating_Scanned_Userfile_List.json", Unique=True)

    # print("Pulling Tweet Threads")
    # Go through User_Tweet_filelist for all tweets that have IDs in the reply or quoted list,
    # or are the replies or quote tweets themselves

    # from Tweet_File_Analysis_Functions import Get_Tweets_By_IDList, Scan_Files_For_Thread_Items
    #
    # for root, dirs, files in os.walk("data"):
    #     for file in files:
    #         if file.startswith('Relevant_User_Tweets_Scanned'):
    #             Relevant_Tweets_From_List_File = "data\\" + file
    # Thread_Outfile = "Data\Thread_Tweets_Scanned_at_" + str(time.time()) + ".json"
    # Thread_Item_Count = Scan_Files_For_Thread_Items(Get_Reply_TweetID_List(Relevant_Tweets_From_List_File),
    #                                                 User_Tweet_filelist, Thread_Outfile)

    # print(Thread_Item_Count)

# TODO: check other files to see if any are that parents, and mark those tweets as relevant as well.





# TODO:

# TODO:

    # Scan relevant tweet file to get users:

# I will need to find replies to and quotes of any tweet in that set in the given time frame. (For that I need IDs.)