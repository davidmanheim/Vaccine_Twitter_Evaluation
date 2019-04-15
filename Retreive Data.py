__author__ = 'dmanheim'

import twitter

import oauth2 as oauth
import time
import json
from PrivateKeys import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET


def get_tweets(api=None, screen_name=None):
    timeline = api.GetUserTimeline(screen_name=screen_name, count=200)
    earliest_tweet = min(timeline, key=lambda x: x.id).id
    print("getting tweets before:", earliest_tweet)

    while True:
        tweets = api.GetUserTimeline(
            screen_name=screen_name, max_id=earliest_tweet, count=200
        )
        new_earliest = min(tweets, key=lambda x: x.id).id

        if not tweets or new_earliest == earliest_tweet:
            break
        else:
            earliest_tweet = new_earliest
            print("getting tweets before:", earliest_tweet)
            timeline += tweets

    return timeline


def get_followers(api=None, screen_name=None):
    users = api.GetFollowers(screen_name=screen_name) #Should be using User IDs, ideally.
    return users


if __name__ == "__main__":
    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
    )
    screen_name = "WHO_VSN"
    print(screen_name)
    VSN_Memberlist = get_followers(api, screen_name)

    # print([u.screen_name for u in VSN_Memberlist])

    for u in VSN_Memberlist:
        timeline = get_tweets(api=api, screen_name=screen_name)

        # Should I create a per-user file?

        with open('tweet_data.json', 'w+') as f:
            for tweet in timeline:
                f.write(json.dumps(tweet._json))
                f.write('\n')


    # I will need to find replies to and quotes of any tweet in that set in the given time frame. (For that I need IDs.)

#
# url='https://api.twitter.com/oauth2/token'
#
# params = {
#     'Authorization': 'OAuth',
#     'oauth_version': '1.0',
#     'oauth_signature': "FVSZ00UtQ4qZssI2Q9c%2BwO%2ByeGo%3D",
#     'oauth_signature_method': "HMAC-SHA1",
#     'oauth_token': 'vVxk5zekIm3CCghU991CqOXha',
#     'oauth_nonce': oauth.generate_nonce(),
#     'oauth_timestamp': str(int(time.time())),
#     'grant_type': 'client_credentials'
# }
#
#
#
# # Set our token/key parameters
# params['oauth_token'] = token.key
# params['oauth_consumer_key'] = consumer.key
#
# # Create our request. Change method, etc. accordingly.
# req = oauth.Request(method="GET", url=url, parameters=params)
#
# # Sign the request.
# signature_method = oauth.SignatureMethod_HMAC_SHA1()
# req.sign_request(signature_method, consumer, token)
#
# # Create our client.
# client = oauth.Client(consumer)
#
# user_follower_url = 'https://api.twitter.com/1.1/followers/ids.json'
#
# #Get Followers.
# user = "WHO_VSN"
# resp, VSN_Members = client.request(user_follower_url  + '?' + 'user_id='+ str(user), "GET")
#
# rate_url='https://api.twitter.com/1.1/application/rate_limit_status.json'
# resp, rates = client.request(rate_url+'?'+'resources=help,users,search,statuses', "GET")
# print(rates)
#
# #We also want the tweets everyone has sent.
#
# #First, a more complete list of WST accounts;
#
# # Request token URL for Twitter.
# list_members_url = "https://api.twitter.com/1.1/lists/members.json"
# WST_List_query_details = 'slug=x-of-y1&owner_screen_name=Voidjumper&&count=200&cursor=-1'
# #This is the list of people in Grognor's WST list.
#
# # Create our client.
# client = oauth.Client(consumer)
#
# #Get it;
# resp, WST_Accounts = client.request(list_members_url + '?' + WST_List_query_details, "GET")
#
# #Write this to a file;
# file=open('Voidjumper_WST_List.json','w')
# file.write(WST_Accounts)
# file.close()
#
#
# #For each account, I want their tweets.
# #First, get the accounts;
#
# WST_List =[{'id':user['id'], 'statuses_count': user['statuses_count'],'screen_name':user['screen_name'],'favs':user['favourites_count']} for user in json.loads(WST_Accounts)['users']]
