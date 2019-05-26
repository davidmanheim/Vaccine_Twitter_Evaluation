__author__ = 'dmanheim'


import twitter
import json
from PrivateKeys import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET


# This fails because it runs lots of separate requests. Need to batch / figure out what to do?

def get_followers(api=None, screen_name=None):
    users = api.GetFollowers(screen_name=screen_name) #Should be using User IDs, ideally.
    return users

# Build a data structure to store this, ideally.

if __name__ == "__main__":
    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True
    )
    screen_name = "WHO_VSN"
    VSN_Memberlist = get_followers(api, screen_name)
    print(VSN_Memberlist)

    with open('WHO_VSN_Member_Followers.json', 'w+') as f:
        for u in VSN_Memberlist: #VSN_Memberlist:
            #Followers = get_followers(api, screen_name=u.screen_name)
            f.write(json.dumps(u))
            f.write('\n')
            #f.write(json.dumps(Followers))
            #f.write('\n')