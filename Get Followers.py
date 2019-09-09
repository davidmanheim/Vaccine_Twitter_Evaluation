__author__ = 'dmanheim'

import time
import twitter
import json
from PrivateKeys import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET


# This fails because it runs lots of separate requests. Need to batch / figure out what to do?

def get_followers(api=None, Userid=None):
    Wait = True
    # Don't hit timeout limit!
    follower_calls = api.CheckRateLimit('/followers/ids')[1]
    friend_calls = api.CheckRateLimit('friends/ids')[1]
    while Wait:
        if min(follower_calls, friend_calls) < 13:  # Kludge-y, but should work...
            print("Waiting before starting user. Calls remaining:", min(follower_calls, friend_calls))
            time.sleep(60.1)
        if min(follower_calls, friend_calls) < 11:
            time.sleep(120.1)
        if min(follower_calls, friend_calls) < 5:
            time.sleep(420.1)
        Wait = False
    try:
        print("get followers")
        Followerlist = list()
        MoreFollowers=True
        Friendlist = list()
        MoreFriends = True
        curr_cursor = -1
        while MoreFollowers:
            follower_calls = api.CheckRateLimit('/followers/ids')[1]
            if follower_calls < 5:
                print("Waiting while getting Followers. Calls remaining:", min(follower_calls, friend_calls))
                time.sleep(420.1)
            addme=api.GetFollowerIDsPaged(user_id=Userid, cursor=curr_cursor)
            curr_cursor = addme[0]
            if curr_cursor == 0:
                MoreFollowers=False
            Followerlist.extend(addme[2])
            follower_calls = follower_calls - 1

        print("get friends")
        curr_cursor = -1
        while MoreFriends:
            friend_calls = api.CheckRateLimit('/friends/ids')[1]
            if friend_calls < 5:
                print("Waiting while getting Friends. Calls remaining:", min(follower_calls, friend_calls))
                time.sleep(420.1)
            addme = api.GetFriendIDsPaged(user_id=Userid, cursor=curr_cursor)
            curr_cursor = addme[0]
            if curr_cursor == 0:
                MoreFriends = False
            Friendlist.extend(addme[2])
            friend_calls = friend_calls - 1

    except twitter.error.TwitterError as TE:
        print("Error for user: ", str(Userid))
        if TE.message == "Not authorized.":
            print("Not authorized, next.")
            Followerset_Tuple = (None, [], [])
            return Followerset_Tuple
        #    print('Cannot get user', user)
            #with open('Skipped.json', 'a') as f:
            #    f.write(json.dumps(Userid))
            #    f.write('\n')
            #    print("Badness")
        #return (Userid, list(), list())
    Followerset_Tuple=(Userid, Followerlist, Friendlist)
    return Followerset_Tuple

# Build a data structure to store this, ideally.

def GetListFile(File):  # Given a file that is a list, get items
    f = open(File, 'r')
    List_from_file=list()
    for line in f:
        List_from_file = json.loads(line)
    f.close()
    return(List_from_file)

def WriteNewList(Input, File): # Removes anything already there!
    with open(File, 'w+') as f:
        f.write(json.dumps(Input))


if __name__ == "__main__":

    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, tweet_mode='extended'
        # , sleep_on_rate_limit=True #Fixed with kludge instead, since this fails.
    )

    api.InitializeRateLimit()

    # VSN_Memberlist = get_followers(api, "WHO_VSN") # For Reference
    # print(VSN_Memberlist)

    #file = open('Updating_User_List_Retrieved_Followers.json', 'w+')
    #file.close()

    List_To_Get_Followers = GetListFile('Updating_Pulled_Exclude_IDs.json')
    #print(List_To_Get_Followers)
    #Check That List against Retreived Follower List
    Updating_User_List_Retreived_Followers = GetListFile('Updating_User_List_Retrieved_Followers.json')

    # Follower_data.json - This is where we append (additional) user follower data retrieved.
    # Create:         f = open('Follower_data.json', 'w+'); f.write(json.dumps([])); f.close()
    follower_calls = 5
    friend_calls = 5
    # @CDCgov times out. Fixed.
    # Guardian would take 30-40 hours to get followers, so it's excluded by necessity.
    # Ditto for Time, 14293310
    # Ditto for Eagles, 180503626
    for user in List_To_Get_Followers:
        if user not in Updating_User_List_Retreived_Followers:
            print("Get Follow items for", str(user))
            Current, Follows, Followed_by = get_followers(api, Userid=user)
            if Current is not None:
                follower_calls = follower_calls + 1
                friend_calls = friend_calls + 1
                print("Data for ", str(user), "Retrieved, now writing to file.")
            Updating_User_List_Retreived_Followers.append(user)
            WriteNewList(Updating_User_List_Retreived_Followers, 'Updating_User_List_Retrieved_Followers.json')
            if Current is not None:
                with open('Follower_data.json', 'a') as f:
                    print("Write 1")
                    towrite = [user, "Following", Follows]
                    f.write(json.dumps(towrite))
                    f.write('\n')
                    print("Write 2")
                    towrite = [user, "FollowedBy", Followed_by]
                    f.write(json.dumps(towrite))
                    f.write('\n')
                    f.close()

            #a = api.CheckRateLimit('%s/followers/ids.json')
            #b = api.CheckRateLimit('%s/friends/ids.json')
            #print("Rate remaining for followers:", a, "with count", follower_calls, "and for friends:", b,
            #      "with count", friend_calls)
        else:
            print("Skipping", str(user))

# Special for CDCgov, which has too many followers.
# ID = 146569971

# Excluding The Guardian manually: 87818409 (8.4m followers)