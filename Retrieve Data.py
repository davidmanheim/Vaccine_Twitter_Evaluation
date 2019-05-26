__author__ = 'dmanheim'

import twitter
import time
# import oauth2 as oauth
# import time
import json
from PrivateKeys import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET


# This script retrieves the initial dataset of tweets from members of the WHO VSN list.

def get_tweets(api=None, screen_name=None, Userid=None):
    if Userid==None:
        timeline = api.GetUserTimeline(screen_name=screen_name, count=200, include_rts=1)
        try:
            earliest_tweet = min(timeline, key=lambda x: x.id).id
        except ValueError:
            print('No earliest Tweet for user')
            return 0
        print("getting tweets before:", earliest_tweet, " for user:", screen_name)

        while True:
            tweets = api.GetUserTimeline(
                screen_name=screen_name, max_id=earliest_tweet, count=200, include_rts=1
            )
            new_earliest = min(tweets, key=lambda x: x.id).id

            if not tweets or new_earliest == earliest_tweet:
                break
            else:
                earliest_tweet = new_earliest
                print("getting tweets before:", earliest_tweet)
                timeline += tweets
    else:
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

        print("getting tweets before: ", earliest_tweet, " for user: ", Userid)

        while True:
            try:
                tweets = api.GetUserTimeline(
                    user_id=Userid, max_id=earliest_tweet, count=200, include_rts=1
                )
            except twitter.error.TwitterError as TE:
                print("Error for user: ", Userid)
                if TE.message == "Not authorized.":
                    print("Not authorized, next.")
                    return 0
                elif "Rate limit" in TE:
                    print('sleeping of 15 minutes')
                    time.sleep(60 * 15)
                    pass
                return 0
            try:
                new_earliest = min(tweets, key=lambda x: x.id).id
            except ValueError:
                print('No more earliest Tweet for user')
                break
            if not tweets or new_earliest == earliest_tweet:
                break
            else:
                earliest_tweet = new_earliest
                print("getting tweets before:", earliest_tweet)
                timeline += tweets
    return timeline


def get_followers(api=None, screen_name=None):
    users = api.GetFollowers(screen_name=screen_name)  # Should be using User IDs, ideally.
    return users


def run_initial():
    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True
    )
    screen_name = "WHO_VSN"
    print(screen_name)
    VSN_Memberlist = get_followers(api, screen_name)

    # We list what we have already, to exclude them.
    Retrieved = {'dfeatamr', 'Diamantius', 'JiayaoL', 'filiamd', 'MamasMaestras', 'VirologyComics', 'CaringforKids',
                 'DrSusanNasif', 'LightForRiley', 'Utzy101', 'MenBAction', 'duronronron', 'mirkoclaus', 'aspsnb0816',
                 'SBohtToutant', 'SarahIOW', 'MaddieScomms', 'GrupoNumoca', 'snehiil', 'EpiRen', 'iboostimmunity',
                 'sabinvaccine', 'okpedaniels', 'GuciGC', 'Muhamma56627761', 'aneinternationa', 'Navaneetlovein1',
                 'tina_maryland', 'INTREPYLLC', 'loic_pfister', 'rajatgarg123', 'travelhealthdoc', 'PergamIC',
                 'clinicaimunita', 'justindknott', 'prof_brunt', 'ThomsonAngus', 'ChandniSondagar', 'NHSImmuniseScot',
                 'NotClickbat', 'danyalmartin', 'D_Lawrencium_G', 'keepgoi16968144', 'IIBCE', 'maimaikelly',
                 'mariojpanelli', 'BPalache', 'Epiconcept', 'HSEschoolsteam', 'chersvacca', 'AMurrayAuthor', 'KongKhL',
                 'NAV_igator', 'nurSYS', 'mratna_chai', 'PaolaCella3', 'drvikasmadaan', 'VaccineUK', 'Immunize_USA',
                 'HealthHarmonie', 'sineadorourke', 'jennifermiram18', 'MeaslesRubella', 'carlosdsuze', 'immunifyme',
                 'Finnpal', 'cat_stacey', 'katejb', 'BTCOConnor', 'CVN_UK', 'CAinexile', 'VEC_ubc', 'roberto_ieraci',
                 'ConRubellaSyndr', 'mdkimhsdubai', 'parismalou', 'SorayaCastroLL', 'TellurianBoy', 'FaziaTadount',
                 'zammit_marc', 'CANImmunize', 'DrNancyM_CDC', 'yurukov', 'huangwt', 'HealthWatch123', 'adadecarom',
                 'LaSF2H', 'merusheel', 'Eilidh257', 'TheBag70', 'Vaccinologist', 'MamaEn_Apuros', 'kath2cats',
                 'TeddyFreddy11', 'gyncsm', 'PepePediatre', 'StorageVaccines', 'Imms_Emma', 'JustynaMajek', 'MamasPara',
                 'SCaplinskas', 'jhaywoodcollett', 'LupeCastillo8', 'HelenEBedford', 'jcjimenop', 'jvalaball',
                 'juana_2012', 'DayaniGalato', 'Anya_Nori', 'DefeatDD', 'saranyavac', 'MrBGRK', 'Dr_roguetwo',
                 'designoversense', 'lehnent', 'kobaprio', 'DanaMur2', 'olga_rostkowska', 'TFX201X', 'olgmns',
                 'mona20_mona', 'ShotAtLife', 'PCIssuesAnswers', 'Dont_Go_Viral', 'Virginiatey', 'Lab_Diagnostics',
                 'NICU_doc_salone', 'RobbButler2', 'VaccinesEurope', 'tptrnn', 'ACT4Meningitis', 'basiaopalska',
                 'precioussoul07', 'Alireza26662033', 'rubialexat', 'SE_Mamelund', 'Pediatra2punto0', 'eddiedacosta2',
                 'DraAChvez', 'Doctors_NS', 'ToniPdevacunas', 'elisantosdorado', 'mmgassociati', 'MeissaVaccines',
                 'h3mclean', 'ZulfiqarEpi', 'vaccines4life', 'NilzaRojasA', 'DrToddWo', 'VacciniRIV', 'InfluenzaHub',
                 'azdi_16', 'Rosybel69', 'alahari_lokesh', 'RESCEUproject', 'EileenRushe', 'ImmunizeCOKids', 'luppi_n',
                 'ClarMaure', 'Adiela_SV', 'RachMacIntosh85', 'MeningitisCA', 'Gringrid', 'YTotskaya', 'PriscillaLynch',
                 'ChrisNorley', 'healthykids11', 'drlucydeng', 'maldonaitsabes', 'SophieCremen', 'Doctorshaib',
                 'doinaazoicai', 'Vaxyourfam', 'marisolfarma', 'RachelAlter007', 'AlokBhatia2008', 'cima_study',
                 'stephcru', 'UNjobs', 'learntherisks', 'AidGanesh', 'Petekash2', 'PEI_Germany', 'ahmrc',
                 'PrecVaccProgram', 'finnegag', 'WichmannOle', 'Kamlashankerv', 'KaitlinSundling', 'ConPediatriaSLP',
                 'Johnmcg26591878', 'IDEpiPhD', 'EpicHealthNews', 'pinabertoglia', 'PaulVanBuynder', 'NedretEmiroglu',
                 'BactiVac', 'pugliesemd', 'karieyoungdahl', 'adelebaleta', 'COMOmeningitis', 'Dorota_M_Wojcik',
                 'SAFIAIB38469578', 'rolandoug', 'StilesJoseph', 'BallatoEdson', 'HPVBoard', 'Saapedispenser',
                 'soyrami', 'UnityConsortium', 'Pame_Q', 'MaireadOConnor8', 'naveenthacker', 'TaubertLab',
                 'MichaelBuratovi', 'The_ISHA', 'MartinaAnzaghe', 'Bhanwar41283624', 'Vaccination_UK', 'wouterhavinga',
                 'CaScreen_carrie', 'IPitcher', 'MVT_InnoFund', 'carlyweeks', 'JoTrust', 'TakeThatChem',
                 'SuffolkImmsTeam', 'edsonsinuhe', 'samicarlson', 'H_HongPhD', 'FrkGiovanetti', 'ThisIsCANVax',
                 'AngelesRzvz', 'simonsdlj', 'kimmykims33', 'JacoboMendioroz', 'SciencePharmer', 'FormularyIE',
                 'nancycampen', 'midha_abhishek', 'ARahman_300', 'DrJennersHouse', 'CWPTSolihullImm', 'LaycockSandra',
                 'InfovacFrance', 'DrSaiSatish', 'jobiebudd', 'marietcasey', 'ZuhurBalayah', 'APPGVaccination',
                 'SoniaBoender', 'hschlent', 'ImmunizeTXW', 'mfprada', 'Larry_Svenson', 'Atlantis1331', 'cacupc',
                 'VaccinateIN', 'jackihartley', 'CFragilite', 'pharmamafia', 'drive_eu', 'tapasnair', 'rishmy2',
                 'OjamaaMikk', 'MongeHernando', 'Mariagreene8', 'historyvaccines', 'Minozennn', 'NIZP_PZH',
                 'JejeLouvetou', 'HenningTveit', 'ahbsam6', 'vaccines411', 'STOPmeningitis', 'LafayettePHNerd'}

    Remaining = [u for u in VSN_Memberlist if u.screen_name not in Retrieved]

    # print([u.screen_name for u in Memberlist_Subset])

    with open('tweet_data.json', 'w+') as f:
        for u in Remaining:  # VSN_Memberlist:
            # Need to check if protected!
            # Also, crashes when user has never tweeted, i.e. Feli56686027 - I now check for that.
            # Also, it crashes anyways and I'm doing this in multiple steps / files.

            if not u.protected:
                if u.statuses_count > 0:
                    timeline = get_tweets(api=api, screen_name=u.screen_name)

                    # Should I create a per-user file?
                    for tweet in timeline:
                        f.write(json.dumps(tweet._json))
                        f.write('\n')

                    # Get Rate data and sleep if we're too close.
                    # time.sleep(15) #Wait a quarter minute per user so that the rate limit isn't hit.
                    # This is a ridiculous hack. Fixed by changing the API interface to sleep on hitting rate limit

        # I will need to find replies to and quotes of any tweet in that set in the given time frame. (For that I need IDs.)


# This dataset includes tweets before & after our intended timeline. It needs to be filtered.


# These are now in a file, and it uses IDs, not screen names.
#     Replied_To = []

if __name__ == "__main__":
# run_initial() # Did this already

    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True
    )



    # I need to fetch data for all users in Replied_To
    # It contains duplicates, and may have users whose data was already retrieved.
    Excluded_file = open("Updating_Pulled_Exclude_IDs.json", 'r')
    for line in Excluded_file:
        excludeIDs = json.loads(line)
    Excluded_file.close()
    ReplyID_file = open("Initial_Replied_IDList.json", "r")
    for line in ReplyID_file:
        Replied_To_ID = json.loads(line)
    ReplyID_file.close()

    for userID in Replied_To_ID:
        # Need to check if protected!
        # Also, crashes when user has never tweeted, i.e. Feli56686027 - I now check for that.
        # Also, it crashes anyways and I'm doing this in multiple steps / files.

        if userID not in excludeIDs:
            timeline = get_tweets(api=api, Userid=userID)
            if timeline==0:
                print("Skipping this, excluding user.")
            else:
                OutFile = "Data\Tweets" + str(userID) + ".json"
                with open(OutFile, 'a') as f:
                    for tweet in timeline:
                        f.write(json.dumps(tweet._json))
                        f.write('\n')
                            # Get Rate data and sleep if we're too close.
                            # time.sleep(15) #Wait a quarter minute per user so that the rate limit isn't hit.
                            # This is a ridiculous hack. Fixed by changing the API interface to sleep on hitting rate limit
                excludeIDs.append(userID)
            with open("Updating_Pulled_Exclude_IDs.json", 'w+') as f:
                f.write(json.dumps(excludeIDs)) #Replace old list with new one. If there is a crash, this helps!

# I will need to find replies to and quotes of any tweet in that set in the given time frame. (For that I need IDs.)