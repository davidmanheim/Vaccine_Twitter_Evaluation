import json

# I got a lot of data, but then it cut out. I need to get the rest.
#FILE = 'WHO_VSN_tweet_data.json' #for testing, I'm using this, not the full set.
FILES[1] = 'tweet_data_Partial1.json'
FILES[2] = 'tweet_data_Partial2.json'
FILES[3] = 'tweet_data_Partial3.json'
FILES[4] = 'tweet_data_Partial4.json'
FILES[5] = 'tweet_data_Partial5.json'

def pull_users(file_list, ):
    userlist=set()

    for file in file_list:
        with open(file) as json_file:
            for line in json_file:
                tweet = json.loads(line)
                if not tweet["retweeted"]:
                    userlist.add(tweet["user"]["screen_name"])
    return userlist

print(pull_users(FILES))


