from Tweet_File_Analysis_Functions import Get_Users_From_Tweet_Files, Get_FileList_Of_JSON_Files, \
    Classify_User, Get_UserIds_From_UserList_File, Vaccine_Terms, MisInfo_Terms, HealthEd_Terms, All_Terms

from random import random
import json


# Run this after all data is retrieved
import os


if not os.path.isfile('data\Classified_Users_One_line.json'): # I haven't pulled the data yet.
    Filelist = Get_FileList_Of_JSON_Files('data', 'Tweets_by_') # Includes tweets per user file
    Filelist2 = Get_FileList_Of_JSON_Files('data', 'tweets_By_') # Includes thread tweets by ID.

    Filelist.extend(Filelist2)

    Get_Users_From_Tweet_Files(Filelist, 'data\All_User_Userdata.json')

    from itertools import islice

    VSN_Ids = []
    input_file = open('data\List_vsn-members-on-twitter_By_WHO_VSN_at_1559731907.1983075.json', 'r')
    raw_batch = islice(input_file, None)
    for current_line in raw_batch:  # Per Tweet.
        item = json.loads(current_line)
        for user in item:
            VSN_Ids.append(user['id'])

    # Now, our list of things to check:

    User_Classes = {"VSN": VSN_Ids, "Expert": ["Dr.", "Doctor", " md ", "m.d." " md." "research", "professor", "public health"],
                    "Organization": ["Official", "National", "Nonprofit", "Non-Profit", "News", "Hospital", "Department",
                                     "Agency", "Center", "health care", "healthcare", "company", "foundation", "association",
                                     "charity", "organization", "institution"],
                    "HealthEd_Term": HealthEd_Terms}

    Users_Classified = Classify_User("data\All_User_Userdata.json", User_Classes)

    with open("data\Classify_All.json", 'w+') as f:
        for item in Users_Classified:
            f.write("User " + str(item) + ":" + json.dumps(Users_Classified[item]))
            f.write('\n')

    # Now, manually review 5%:
    with open("data\Classify_All.json", 'r') as f, open("data\Manual_Check.json", 'w+') as r:
        # append the batch, and close file each time.
        for line in f:
            if random() < 0.05:
                r.write(line)

    # We'll use Mediawiki to check the URLs provided by users. First, though, we check those URLs.

    Site_for_Verif = 0
    TW_Count = 0
    for item in Users_Classified:
        if Users_Classified[item]['verified']:
            if "Website" in Users_Classified[item].keys():
                if Users_Classified[item]["Website"] is not None:
                    if ("twitter.com" in Users_Classified[item]["Website"]):
                        TW_Count = TW_Count + 1
                    else:
                        Site_for_Verif = Site_for_Verif + 1
                else:
                    Site_for_Verif = Site_for_Verif + 1
    print(TW_Count)
    print(Site_for_Verif)

    with open('data\Classified_Users_One_line.json', 'w+') as r:
        r.write(json.dumps(Users_Classified))
        r.close()

# Now, check wikimedia.

import requests

# response = requests.get("https://www.wikidata.org/w/api.php?action=query&format=json&list=exturlusage&euquery=www.aol.com&euprotocol=https&eunamespace=0")
# resp_data = json.loads(response.text)
#
# response2 = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=wikidatawiki&format=json&ids=" + resp_data['query']['exturlusage'][0]['title'])
# resp2_data = json.loads(response2.text)
# response3 = requests.get("https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&entity=" + resp_data['query']['exturlusage'][0]['title'])
# resp3_data = json.loads(response3.text)
# # I want property P452 - industry.
# resp2_data['entities'][resp2_data['entities'].keys().__iter__().__next__()]['claims']['P452']
# First, check if the company / web site has an entry at all.

def Check_Wikidata(URL):
    if (URL.startswith('https:')):
        URL = URL[8:]
    elif (URL.startswith('http:')):
        URL = URL[7:]
    response = requests.get("https://www.wikidata.org/w/api.php?action=query&format=json&list=exturlusage&euquery=" + URL +"&euprotocol=https&eunamespace=0")
    resp_data = json.loads(response.text)
    if "query" not in resp_data.keys():
      print("Problem with Query.")
      print(URL)
      print(response.text)
    elif len(resp_data['query']['exturlusage'])>0:
        return 1
        # response2 = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=wikidatawiki&format=json&ids=" +
        # resp_data['query']['exturlusage'][0]['title'])
    else:
        return 0

# Now, classify.

def Pull_Wikidata_Type(URL):
    if (URL.startswith('https:')):
        URL = URL[8:]
    elif (URL.startswith('http:')):
        URL = URL[7:]
    response = requests.get("https://www.wikidata.org/w/api.php?action=query&format=json&list=exturlusage&euquery=" +
                            URL +"&euprotocol=https&eulimit=500")
    # For Cnn, this doesn't get me CNN! Argh. Needed to look for HTTP, not HTTPS.
    response_insecure = requests.get("https://www.wikidata.org/w/api.php?action=query&format=json&list=exturlusage&euquery=" +
                            URL + "&euprotocol=http&eulimit=500")
    resp_data = json.loads(response.text)
    resp_insecure_data = json.loads(response_insecure.text)
    data_list = []
    # The function fails for youtube URLs, and presumably others that contain cgi parameters with "="
    if len(resp_data['query']['exturlusage'])>0:
        data_list.extend(resp_data['query']['exturlusage'])
    if len(resp_insecure_data['query']['exturlusage'])>0:
        data_list.extend(resp_insecure_data['query']['exturlusage'])
        # Find the one with the shortest URL. If a tie, find the one with lowest pageid.
    shortlist = [item for item in data_list if len(item['url']) <= min([len(item['url']) for item in data_list])+2]
    # Add 2 for secure / insecure and trailing slash or not.

    if len(shortlist) > 1:
        shortlist = [item for item in shortlist if item['pageid']== min([item['pageid'] for item in shortlist])]
    if len(shortlist) != 0:
        response2 = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=wikidatawiki&format=json&ids=" +
        shortlist[0]['title'])
        resp2_data = json.loads(response2.text)
        if 'entities' in resp2_data.keys():
            Output = resp2_data['entities'][resp2_data['entities'].keys().__iter__().__next__()]
            if 'claims' in Output.keys():
                Output = Output['claims']
            else:
                print("Problem with", URL, "b/c entry has no claims")
        else:
            print("Problem with", URL, "no entity returned")
            return (False)
    else:
        print("For", URL, "no results were returned")
        return(False)

    Out_Str = str(Output)

    if "Q11030" in Out_Str:
        return ("News")
    elif "Q11032" in Out_Str:
        return ("News")
    elif "Q11033" in Out_Str:
        return ("News")
    elif "Q192283" in Out_Str:
        return ("News")
    elif "Q41298" in Out_Str:
        return ("News")
    elif "Q2305295" in Out_Str:
        return ("News")
    elif "Q1002697" in Out_Str:
        return ("News")
    elif "Q1616075" in Out_Str: #TV Station
        return ("News")
    elif "Q1110794" in Out_Str:
        return ("News")
    elif "Q8513" in Out_Str:
        return ("Data Source")
    elif "Q31855" in Out_Str:
        return ("Research Org")
    elif "Q5633421" in Out_Str:
        return ("Research Org")
    elif "Q875538" in Out_Str:
        return ("University")
    elif "Q163740" in Out_Str:
        return ("Nonprofit")
    elif "Q7246202" in Out_Str:
        return ("Nonprofit") # Foundation
    elif "Q4830453" in Out_Str:
        return("Business")
    elif "Q43229" in Out_Str:
        return ("Other Org")
    elif "Q392918" in Out_Str: # EU org.
        return ("Other Org")
    elif "Q484652" in Out_Str: # Int'l org.
        return ("Other Org")
    elif "Q7278" in Out_Str: # Political Party
        return ("Other Org")
    elif "'Q5'" in Out_Str:
        return ("Person")
    else:
        return(None)

    # Check the following.
    #['P452'] - Org Type.
    # I want to check if it is a: Q4830453 Business, Q43229 Organization, Q163740 Nonprofit, etc.
    #['P910'] - Wikimedia category

    # Nice to check: P2002, twitter user name?


if False: #Scraps of code to check the data.

    len([item for item in Users_Classified if Users_Classified[item]['verified']]) # 12,309 users.

    len([item for item in Users_Classified if Users_Classified[item]['verified'] and
        (not (Users_Classified[item]['Expert'] or Users_Classified[item]['Organization'] or Users_Classified[item]['VSN']))])
    # 8406. That makes sense... Lots of verified individuals that aren't experts or organizations.

    len([item for item in Users_Classified if Users_Classified[item]['Organization']])
    len([item for item in Users_Classified if Users_Classified[item]['Organization'] and 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None])

    len([item for item in Users_Classified if Users_Classified[item]['Expert']])
    len([item for item in Users_Classified if Users_Classified[item]['Expert'] and 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None])
    Check = [Users_Classified[item]['Website'] for item in Users_Classified if Users_Classified[item]['Expert'] and 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None]
    len([site for site in Check if ".edu" in site or ".ac." in site])
    len([site for site in Check if ".com" in site or ".co." in site])
    len([site for site in Check if ".org" in site])
    len([site for site in Check if ".gov" in site])
    # This should be a proxy for "personal" sites:
    len([site for site in Check if "/~" in site or "facebook" in site or "twitter" in site or "linkedin" in site
         or "about.me" in site or "academia.edu" in site or "people" in site or "profile" in site or "personal" in site
         or "people" in site or "faculty" in site or "staff" in site or "scholar.google" in site])


    # Redo above checks for orgs:
    Check = [Users_Classified[item]['Website'] for item in Users_Classified if Users_Classified[item]['Organization'] and 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None]
    print(len([site for site in Check if ".edu" in site or ".ac." in site]))
    print(len([site for site in Check if ".com" in site or ".co." in site]))
    print(len([site for site in Check if ".org" in site]))
    print(len([site for site in Check if ".gov" in site]))
    print(len([site for site in Check if ".net" in site]))
    len([site for site in Check if "/~" in site or "linkedin" in site
         or "about.me" in site or "academia.edu" in site or "people" in site or "profile" in site or "personal" in site
         or "people" in site or "faculty" in site or "staff" in site or "scholar.google" in site])

    len([item for item in Users_Classified if Users_Classified[item]['Expert'] and Users_Classified[item]['Organization']])


    Websites = [Users_Classified[item]['Website'] for item in Users_Classified if 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None]

# Check_Wikidata(Websites[0]) # If so, we assume they are an actual org. (We check this later.)
# If not, it gives us no info.

#How many are left to do?

len([item for item in Users_Classified if 'Website' in Users_Classified[item].keys() and
     Users_Classified[item]['Website'] is not None and "Wikidata" not in Users_Classified[item].keys()])


# Only runs for sites / users not already checked.

count = 1
skip = 1
import time
for item in Users_Classified:
    if 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None:
        if "Wikidata" in Users_Classified[item].keys():
            skip = skip + 1
        else:
            Wikidata_Check = (Check_Wikidata(Users_Classified[item]['Website']) == 1) # True/False
            Users_Classified[item]["Wikidata"] = Wikidata_Check
            count = count+1
        if (skip % 1000) == 0:
            print("skipped total of:", skip)
        if (count%50) == 0:
            print("Count: ", count)
        if count % 1000 == 0:
            print("Wait a minute!")
            time.sleep(60)


if False: # More checks.
    len([Users_Classified[item] for item in Users_Classified if "Wikidata" in Users_Classified[item].keys()])

    len([Users_Classified[item] for item in Users_Classified if "Wikidata" in Users_Classified[item].keys() and Users_Classified[item]["Wikidata"]])
    # Only 1094
    len([Users_Classified[item] for item in Users_Classified if "Wikidata" in Users_Classified[item].keys() and not Users_Classified[item]["Wikidata"]])

    len([Users_Classified[item] for item in Users_Classified if "Wikidata" in Users_Classified[item].keys() and Users_Classified[item]["verified"] and Users_Classified[item]["Wikidata"]])

    len([Users_Classified[item] for item in Users_Classified if "Wikidata" in Users_Classified[item].keys() and Users_Classified[item]["Wikidata"] and not Users_Classified[item]["verified"]])

    # Now we can check wikidata for actual info on sites we have info about.
    Sites_With_Wikidata = [Users_Classified[item]["Website"] for item in Users_Classified if "Wikidata" in Users_Classified[item].keys() and Users_Classified[item]["Wikidata"]]


# Now pull data on org types.

count = 1
for user in Users_Classified:
    if "Wikidata" in Users_Classified[user].keys() and Users_Classified[user]["Wikidata"] and \
            "Wikidata_Class" not in Users_Classified[user].keys(): # Don't rerun unnecessarily!
        Users_Classified[user]["Wikidata_Class"] = Pull_Wikidata_Type(Users_Classified[user]["Website"])
        count = count + 1
        if count%25 == 0:
            print("Count: ", count)
# It's clear that this captures a bunch of orgs that don't get captured by keywords, especially non-english orgs.
# These get captured well by Wikidata, though!

# Saved error log via print() to data folder.

with open("data\Classified_Users_With_Wikimedia_One_line.json", 'w+') as r:
    r.write(json.dumps(Users_Classified))
    r.close()

with open("data\Classified_Users_With_Wikimedia_One_line.json", 'r') as r:
    Users_Classified = json.loads(r.readline())

# Rules:
# Wikimedia IDs are used for news.


# Use BotOrNot / Botometer:
# Code adapted from https://github.com/IUNetSci/botometer-python

import botometer
from PrivateKeys import Bot_or_Not_headers as headers, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, \
    CONSUMER_SECRET

rapidapi_key = headers['x-rapidapi-key']

twitter_app_auth = {
    'consumer_key': CONSUMER_KEY,
    'consumer_secret': CONSUMER_SECRET,
    'access_token': ACCESS_TOKEN_KEY,
    'access_token_secret': ACCESS_TOKEN_SECRET,
}

bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)


# Test_Users = list(Users_Classified.keys())[0:10]
# for UserID, result in bom.check_accounts_in(Test_Users):
#    Users_Classified[UserID]['BotOMeter'] = result

def Run_100_More_BotOrNot_Queries():
    Users_so_far = 0
    To_get = [key for key in list(Users_Classified.keys())] # if 'BotOMeter' not in Users_Classified[key].keys()]
    for UserID, result in bom.check_accounts_in(To_get[0:100]):
        # print(result)
        if "error" in result.keys():
            Users_Classified[UserID]['BotOMeter'] = -1
        else:
            Users_Classified[UserID]['BotOMeter'] = result['cap']['english']
            Users_Classified[UserID]['BotOMeter_Scores'] = result
        Users_so_far = Users_so_far + 1
        if (Users_so_far + 1) % 20 == 0:
            print("So Far, ", Users_so_far)


# Failure_Item = [key for key in list(Users_Classified.keys()) if 'BotOMeter' not in Users_Classified[key].keys()][0]

# Started 10:37 AM.
# At 10:40, 39.
# Projected 40/3 minutes, 12,000 total, 3*12,000/40 = 900 minutes = 15 hours. :(
# At 10:42, 59.
# Projected 60/5 minutes, 12,000 total, 5*12,000/60 = 1,000 minutes = 16.67 hours. :((((
# ... Ended / Died. Hmmm....?
# Dies on error (These all seem to be deleted accounts). This was addressed by adding - if "error" in result.keys():

if os.path.isfile("data\Classified_Users_With_BotOrNot_One_line.json"):
    with open("data\Classified_Users_With_BotOrNot_One_line.json", 'r') as r:
        Users_Classified = json.loads(r.readline())
        r.close()

for i in range(1, 121):  # This runs 12,100, which should be everyone.
    # It will likely need to be killed first - but the data is persistent in the object.
    # I should write it itermittently!
    print("Set #", i)
    Run_100_More_BotOrNot_Queries()
    with open("data\Classified_Users_With_BotOrNot_One_line.json", 'w+') as r:
        r.write(json.dumps(Users_Classified))
        r.close()

# Started 11:30 AM.
# Set #1, 19 at 11:31.
# Set #1, 99 at 11:39 - 100/9 minutes, 12,000 total, 9*12,000/100 = 1,080 minutes = 18 hours. :((((

Pulled_keys = [key for key in Users_Classified.keys() if 'BotOMeter' in Users_Classified[key].keys()]
len(Pulled_keys) # 451 at initial testing.
Users_BotChecked = dict()
for key in Pulled_keys:
    Users_BotChecked[key] = Users_Classified[key]

len([item for item in Users_BotChecked if Users_BotChecked[item]['verified']])

for item in Users_BotChecked:
    if Users_BotChecked[item]['verified']:
        print(Users_BotChecked[item])

for item in Users_BotChecked:
    if Users_BotChecked[item]['BotOMeter']>0.5:
        print(item, Users_BotChecked[item])

for item in Users_BotChecked:
    if Users_BotChecked[item]['BotOMeter'] > 0.5 and Users_BotChecked[item]['verified']:
        print(item, Users_BotChecked[item])



#I have some weird things here. "Bot" user 16258903 didn't tweet in 2018...

