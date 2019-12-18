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

    # Nice to check: P2002, twitter user name? Very rarely available, not reliably the same (orgs have multiple accounts)


if False: #Scraps of code to check the data.

    len([item for item in Users_Classified if Users_Classified[item]['verified']]) # 12,309 users.

    len([item for item in Users_Classified if Users_Classified[item]['verified'] and
        (not (Users_Classified[item]['Expert'] or Users_Classified[item]['Organization'] or Users_Classified[item]['VSN']))])
    # 8406. That makes sense... Lots of verified individuals that aren't experts or organizations.

    len([item for item in Users_Classified if Users_Classified[item]['Organization']])
    len([item for item in Users_Classified if Users_Classified[item]['Organization'] and 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None])

    len([item for item in Users_Classified if Users_Classified[item]['Expert']])
    len([item for item in Users_Classified if Users_Classified[item]['Expert'] and 'Website' in Users_Classified[item].keys() and Users_Classified[item]['Website'] is not None])

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
    r.close()

# Rules:
# Wikimedia IDs are used for news.

def DomainEnding(URL,Ending): #Check if the Domain ends with any of the Endings listed.
    if type(Ending) == type("string"):
        Ending=[Ending]
    for End in Ending:
        if End[0] != ".":
            End = "." + End # "org" needs to be ".org"
        if End[-1] == "." or End[-1] == "/": # Covers ".org.uk" or ".org/" matching ".org"
            if End in URL:
                return(True)
        elif (End+".") in URL: # Covers ".org.uk". "www.com.net" will be wrong, not "dotcom.net", as it starts with "."
            return(True)
        elif (End+"/") in URL:
            return(True)
        elif URL[(-1*len(End)):]==End: #No trailing slash, but it's the end of the URL
            return(True)
    return(False)

DomainEnding("www.aol.com",[".com"])


def Infer_Type(URL):
    if DomainEnding(URL, [".edu", ".ac."]): #.ac by itself is a cTLD.
        return("Academic")
    if "/~" in URL or "facebook" in URL or "twitter" in URL or "linkedin" in URL \
        or "about.me" in URL or "academia.edu" in URL or "people" in URL or "profile" in URL or "personal" in URL \
        or "people" in URL or "faculty" in URL or "staff" in URL or "scholar.google" in URL:
        return("Personal")
    if DomainEnding(URL, [".com", ".co."]):
        return("Company")
    if DomainEnding(URL, [".gov", ".mil"]):
        return("Government")
    if DomainEnding(URL, [".org", ".net", ".int"]):
        return("Organization")
    return("Unknown") #Otherwise

# Now, Classify:
for user in Users_Classified:
    if int(user) in VSN_IDs:
        Users_Classified[user]['Heuristic Class'] = "VSN"
    elif "Wikidata_Class" in Users_Classified[user].keys():
        Users_Classified[user]['Heuristic Class'] = Users_Classified[user]["Wikidata_Class"]
    elif 'Website' in Users_Classified[user].keys() and Users_Classified[user]['Website'] is not None:
        Users_Classified[user]['Heuristic Class'] = Infer_Type(Users_Classified[user]['Website'])
    else:
        Users_Classified[user]['Heuristic Class'] = "Unknown"


# Checks:
len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()]) #37811

len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="VSN"]) # 53. Good.

len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="Unknown"]) # 9577

Unknowns = [item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys() and
            Users_Classified[item]['Heuristic Class']=="Unknown"]
for user in Unknowns[301:325]:
    print(Users_Classified[user]['Website'])
    #Most are

len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="Academic"]) # 788 #Academic trumps personal;
len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="Personal"]) # 2871
len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="Company"]) # 17083
len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="Organization"]) # 4051
len([item for item in Users_Classified if 'Heuristic Class' in Users_Classified[item].keys()
     and Users_Classified[item]['Heuristic Class']=="Government"]) # 523


with open("data\Fully_Classified_Users_One_line.json", 'w+') as r:
    r.write(json.dumps(Users_Classified))
    r.close()

with open("data\Fully_Classified_Users_One_line.json", 'r') as r:
    Users_Classified = json.loads(r.readline())
    r.close()

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

def Run_More_BotOrNot_Queries(To_get):
    Users_so_far = 0
    for UserID, result in bom.check_accounts_in(To_get):
        # print(result)
        if "error" in result.keys():
            Users_Classified[UserID]['BotOMeter'] = -1
            print(result['error'])
        else:
            Users_Classified[UserID]['BotOMeter'] = result['cap']['english']
            Users_Classified[UserID]['BotOMeter_Scores'] = result
        Users_so_far = Users_so_far + 1
        if (Users_so_far + 1) % 20 == 0:
            print("So Far, ", Users_so_far)

def Pick_Up_Stragglers():
    Stragglers = list()
    Count_Missing = 0
    for user in AllUserSet:
        if str(user) in Users_Classified.keys():
            if not "BotOMeter" in Users_Classified[str(user)].keys():
                Stragglers.append(str(user))
        else:
            Count_Missing = Count_Missing + 1
    print(str(Count_Missing) + " missing")
    return Stragglers


# Failure_Item = [key for key in list(Users_Classified.keys()) if 'BotOMeter' not in Users_Classified[key].keys()][0]

# Started 10:37 AM.
# At 10:40, 39.
# Projected 40/3 minutes, 12,000 total, 3*12,000/40 = 900 minutes = 15 hours. :(
# At 10:42, 59.
# Projected 60/5 minutes, 12,000 total, 5*12,000/60 = 1,000 minutes = 16.67 hours. :((((
# ... Ended / Died. Hmmm....?
# Dies on error (These all seem to be deleted accounts). This was addressed by adding - if "error" in result.keys():

# But there are 76,000 users in Users_Classified. (Why?)

if os.path.isfile("data\Classified_Users_With_BotOrNot_One_line.json"):
    with open("data\Classified_Users_With_BotOrNot_One_line.json", 'r') as r:
        Users_Classified = json.loads(r.readline())
        r.close()

To_get = [key for key in list(Users_Classified.keys()) if 'BotOMeter' not in Users_Classified[key].keys()]

for i in range(1, 60):  # This runs 76,200, which should be everyone
    # It will likely need to be killed first - but the data is persistent in the object.
    # Write intermittenetly. Looks like this will take a couple weeks to pull all the data.
    print("Set #", i)
    Subset = To_get[0:100]
    To_get = To_get[101:]
    Run_More_BotOrNot_Queries(Subset)
    with open("data\Classified_Users_With_BotOrNot_One_line.json", 'w+') as r:
        r.write(json.dumps(Users_Classified))
        r.close()

# Started 11:30 AM.
# Set #1, 19 at 11:31.
# Set #1, 99 at 11:39 - 100/9 minutes, 12,000 total, 9*12,000/100 = 1,080 minutes = 18 hours. :((((


# Analysis Snippets:
if False:
    Pulled_keys = [key for key in Users_Classified.keys() if 'BotOMeter_Scores' in Users_Classified[key].keys()]
    Pulled_keys = [key for key in Pulled_keys if 'cap' in Users_Classified[key]['BotOMeter_Scores'].keys()]
    print(len(Pulled_keys), " out of ", len(Users_Classified)) # 451 at initial testing.
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

def Redo_100_More_BotOrNot_Queries(): #(When it went offline, the check gives an error, and sets the score to -1.)
    Users_so_far = 0
    Recheck = [key for key in list(Users_Classified.keys()) if 'BotOMeter' in Users_Classified[key].keys()]
    Recheck = [key for key in Recheck if Users_Classified[key]['BotOMeter'] == -1]

    for UserID, result in bom.check_accounts_in(Recheck[0:100]):
        # print(result)
        if "error" in result.keys():
            Users_Classified[UserID]['BotOMeter'] = -1
            print(result['error'])
        else:
            Users_Classified[UserID]['BotOMeter'] = result['cap']['english']
            Users_Classified[UserID]['BotOMeter_Scores'] = result
        Users_so_far = Users_so_far + 1
        if (Users_so_far + 1) % 20 == 0:
            print("So Far, ", Users_so_far)


for i in range(1, 16):  # There were 1,5?? errors, so this should cover it.
    # It will likely need to be killed first - but the data is persistent in the object.
    # Write intermittenetly. Looks like this will take a couple weeks to pull all the data.
    print("Set #", i)
    Redo_100_More_BotOrNot_Queries()
    with open("data\Classified_Users_With_BotOrNot_One_line.json", 'w+') as r:
        r.write(json.dumps(Users_Classified))
        r.close()


############################
####   Analysis Time!   ####
############################

# First, look at just VSN Members:

# Sanity Check:
Badness = 0
for u in Users_Classified:
    i = None
    v = None
    if int(u) in VSN_Ids:
        v = True
    if Users_Classified[u]['VSN']:
        i=True
    if i != v:
        Badness = Badness + 1
# Badness 0 - it matches, once I realized I needed to convert strings to ints.

VSN_Users_Classified = dict()
for u in Users_Classified:
    if int(u) in VSN_Ids:
        VSN_Users_Classified[u] = Users_Classified[u]

def Dicts_Summary(d, entries=None): #Get counts of all items in each entry, plus the values of dicts specified
    Summary = dict()
    for entry in entries:
        Summary[entry] = dict()
    for item in d:
        try:
            for entry in d[item]:
                if type(d[item][entry]) == type(False): # Boolean
                    if entry in Summary:
                        Summary[entry] = Summary[entry] + d[item][entry]
                    else:
                        Summary[entry] = int(d[item][entry])
                if type(d[item][entry]) == type("String"):
                    if entry in entries:
                        if d[item][entry] in Summary[entry]:
                            Summary[entry][d[item][entry]] = Summary[entry][d[item][entry]] + 1
                        else:
                            Summary[entry][d[item][entry]] = 1
        except (TypeError, NameError):
            pass
    return(Summary)

VSN_U_Summary = Dicts_Summary(VSN_Users_Classified, ['Wikidata_Class','Heuristic Class'])
# {'Wikidata_Class': {'Research Org': 2}, 'Heuristic Class': {'Organization': 15, 'Unknown': 22, 'Academic': 1,
# 'Government': 3, 'Company': 3}, 'verified': 12, 'VSN': 53, 'Expert': 6, 'Organization': 16, 'HealthEd_Term': 17,
# 'Wikidata': 6}
# 'Heuristic Class': {'Unknown': 47970, 'VSN': 53, 'Personal': 2874, 'Organization': 4037,
# 'Company': 17071, 'Government': 520, 'Nonprofit': 109, 'Other Org': 170, 'Data Source': 3,
# 'Person': 530, 'Academic': 787, 'News': 557, 'Research Org': 61, 'Business': 169, 'University': 13}




All_U_Summary = Dicts_Summary(Users_Classified, ['Wikidata_Class','Heuristic Class'])
# {'Wikidata_Class': {'Research Org': 63, 'Nonprofit': 109, 'Other Org': 170, 'Data Source': 3, 'Person': 530,
# 'News': 557, 'Business': 169, 'University': 13}, 'Heuristic Class': {'Organization': 4051, 'Unknown': 9594,
# 'Personal': 2871, 'Company': 17063, 'Academic': 788, 'Government': 523}, 'verified': 12039, 'VSN': 53, 'Expert': 2251,
# 'Organization': 8753, 'HealthEd_Term': 1124, 'Wikidata': 2898}


Ver_U_Summary = Dicts_Summary({U:Users_Classified[U] for U in Users_Classified if Users_Classified[U]['verified']}, ['Wikidata_Class'])
#{'Wikidata_Class': {'Research Org': 24, 'Other Org': 85, 'Data Source': 2, 'Person': 316, 'News': 412, 'Business': 106,
# 'Nonprofit': 56, 'University': 11}, 'verified': 12039, 'VSN': 12, 'Expert': 218, 'Organization': 3462,
# 'HealthEd_Term': 103, 'Wikidata': 1817}

Dicts_Summary({U:Users_Classified[U] for U in Users_Classified if Users_Classified[U]['Organization']}, ['Wikidata_Class','Heuristic Class'])


Dicts_Summary({U:Users_Classified[U] for U in Users_Classified if Users_Classified[U]['Expert']}, ['Wikidata_Class','Heuristic Class'])

Dicts_Summary({U:Users_Classified[U] for U in Users_Classified if not Users_Classified[U]['Expert'] and not Users_Classified[U]['Organization']}, ['Wikidata_Class','Heuristic Class'])

# We now have 3 partial classifications: Keyword, Wikimedia, and Domain.
# The order used for classification is: Wikimedia, then Keyword, then Domain.
# (More complex than that, as implemented below. See Methodology.)

#################
# TO DO
#################

for u in Users_Classified:
    if u['']