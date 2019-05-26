import json

# I got a lot of data, but then it cut out. I need to get the rest.
#FILE = 'WHO_VSN_tweet_data.json' #for testing, I'm using this, not the full set.
FILES = list()
FILES.append('tweet_data_Partial1.json')
FILES.append('tweet_data_Partial2.json')
FILES.append('tweet_data_Partial3.json')
FILES.append('tweet_data_Partial4.json')
FILES.append('tweet_data_Partial5.json')

def pull_users(file_list):
    userlist=set()
    print(file_list)
    for file in file_list:
        with open(file) as json_file:
            for line in json_file:
                tweet = json.loads(line)
                if not tweet["retweeted"]:
                    userlist.add(tweet["user"]["screen_name"])
    return userlist

Retrieved = pull_users(FILES)
print(Retrieved)

# List retrieved from Tweet File Read
# Retrieved = ['DrToddWo', 'BalibreaNuria', 'h3mclean', 'CaScreen_carrie', 'SuffolkImmsTeam', 'luppi_n', 'TheBag70', 'LaycockSandra',
#  'InfovacFrance', 'aneinternationa', 'merusheel', 'D_Lawrencium_G', 'Epiconcept', 'Immunize_USA', 'FaziaTadount',
#  'HSEschoolsteam', 'adelebaleta', 'COMOmeningitis', 'NHSImmuniseScot', 'DayaniGalato', 'Vaccinologist',
#  'PrecVaccProgram', 'tina_maryland', 'BallatoEdson', 'DattaChaudhuri', 'rajatgarg123', 'juana_2012', 'tptrnn',
#  'mariojpanelli', 'kath2cats', 'CWPTSolihullImm', 'IPitcher', 'MongeHernando', 'LightForRiley', 'ACT4Meningitis',
#  'ISahinovic', 'JejeLouvetou', 'ConRubellaSyndr', 'IIBCE', 'SBohtToutant', 'ThomsonAngus', 'RachMacIntosh85',
#  'maldonaitsabes', 'jackihartley', 'pinabertoglia', 'HealthWatch123', 'mirkoclaus', 'midha_abhishek', 'INTREPYLLC',
#  'BTCOConnor', 'Utzy101', 'Muhamma56627761', 'AlokBhatia2008', 'xcel_regal', 'pugliesemd', 'KaitlinSundling',
#  'cima_study', 'CVN_UK', 'cacupc', 'katejb', 'muldersm', 'ZulfiqarEpi', 'SorayaCastroLL', 'Pame_Q', 'ZuhurBalayah',
#  'TFX201X', 'adeyeye_eo', 'NedretEmiroglu', 'roberto_ieraci', 'immunifyme', 'jobiebudd', 'NotClickbat', 'naveenthacker',
#  'jvalaball', 'PriscillaLynch', 'elisantosdorado', 'LafayettePHNerd', 'HealthHarmonie', 'PCIssuesAnswers', 'vipintukur',
#  'AMurrayAuthor', 'VaccinesToday', 'PaulVanBuynder', 'Mariagreene8', 'Finnpal', 'Johnmcg26591878', 'SAFIAIB38469578',
#  'AidGanesh', 'ChrisNorley', 'okpedaniels', 'olga_rostkowska', 'jcjimenop', 'kimmykims33', 'nancycampen',
#  'UnityConsortium', 'MartinaAnzaghe', 'SciencePharmer', 'mratna_chai', 'Danielot', 'JiayaoL', 'NICU_doc_salone',
#  'CaringforKids', 'SarahIOW', 'rx_mph', 'ToniPdevacunas', 'travelhealthdoc', 'carlyweeks', 'mdkimhsdubai', 'Gringrid',
#  'Alireza26662033', 'clinicaimunita', 'zuberp1', 'ARahman_300', 'keepgoi16968144', 'maimaikelly', 'Atlantis1331',
#  'Adiela_SV', 'carlosdsuze', 'CANImmunize', 'tapasnair', 'JacoboMendioroz', 'karieyoungdahl', 'sineadorourke',
#  'RESCEUproject', 'basiaopalska', 'edsonsinuhe', 'ChandniSondagar', 'HPVBoard', 'MeissaVaccines', 'wouterhavinga',
#  'IDEpiPhD', 'EpicHealthNews', 'PergamIC', 'EileenRushe', 'VaccinesEurope', 'simonsdlj', 'PEI_Germany',
#  'Bhanwar41283624', 'saranyavac', 'marisolfarma', 'adadecarom', 'MVT_InnoFund', 'LaSF2H', 'eddiedacosta2', 'VacciniRIV',
#  'drvikasmadaan', 'DefeatDD', 'Eilidh257', 'Minozennn', 'Doctors_NS', 'SE_Mamelund', 'RobbButler2', 'stephcru',
#  'Pediatra2punto0', 'ShotAtLife', 'H_HongPhD', 'vaccines4life', 'danyalmartin', 'samicarlson', 'designoversense',
#  'TakeThatChem', 'DrSusanNasif', 'iboostimmunity', 'FormularyIE', 'mfprada', 'Dont_Go_Viral', 'Vaccination_UK', 'NCIRS',
#  'botta_gabriela', 'Frasca74', 'jhaywoodcollett', 'TaubertLab', 'MamasPara', 'NIZP_PZH', 'MamasMaestras', 'UnmeshDr',
#  'ICBDSR', 'HSEImm', 'TellurianBoy', 'GuciGC', 'huangwt', 'VaccineUK', 'KongKhL', 'yurukov', 'dfeatamr',
#  'WHO_Europe_VPI', 'MrBGRK', 'ahbsam6', 'PaolaCella3', 'rubialexat', 'historyvaccines', 'SCaplinskas', 'parismalou',
#  'ThisIsCANVax', 'GrupoNumoca', 'cat_stacey', 'lehnent', 'WichmannOle', 'Lab_Diagnostics', 'GermyGermyGermy',
#  'mmgassociati', 'Imms_Emma', 'MeaslesRubella', 'VaccinateIN', 'StorageVaccines', 'ahmrc', 'duronronron', 'rolandoug',
#  'drlucydeng', 'MichaelBuratovi', 'MamaEn_Apuros', 'Rosybel69', 'JustynaMajek', 'BPalache', 'sabinvaccine', 'BactiVac',
#  'drive_eu', 'VaxResources', 'NilzaRojasA', 'ImmunizeCOKids', 'gyncsm', 'learntherisks', 'DraAChvez', 'prof_brunt',
#  'SophieCremen', 'VEC_ubc', 'The_ISHA', 'Dr_roguetwo', 'olgmns', 'finnegag', 'SoniaBoender', 'vaccines411',
#  'RachelAlter007', 'STOPmeningitis', 'VirologyComics', 'mona20_mona', 'Diamantius', 'alahari_lokesh', 'MaddieScomms',
#  'jennifermiram18', 'MenBAction', 'InfluenzaHub', 'Simozzzzz', 'azdi_16', 'MaireadOConnor8', 'Kamlashankerv', 'UNjobs',
#  'loic_pfister', 'Vaxyourfam', 'DrSaiSatish', 'ImmunizedotCa', 'Larry_Svenson', 'FrkGiovanetti', 'ClarMaure',
#  'Navaneetlovein1', 'soyrami', 'rishmy2', 'StilesJoseph', 'Saapedispenser', 'APPGVaccination', 'LupeCastillo8',
#  'PepePediatre', 'doinaazoicai', 'nurSYS', 'snehiil', 'HelenEBedford', 'TeddyFreddy11', 'CAinexile', 'DrJennersHouse',
#  'Petekash2', 'justindknott', 'OjamaaMikk', 'WalleyRay', 'Dorota_M_Wojcik', 'gloriapagin', 'precioussoul07',
#  'ElIngenieroCha1', 'Virginiatey', 'YTotskaya', 'AngelesRzvz', 'zammit_marc', 'aspsnb0816', 'Doctorshaib', 'chersvacca',
#  'ImmunizeTXW', 'marietcasey', 'DanaMur2', 'healthykids11', 'hschlent', 'DrNancyM_CDC', 'kobaprio', 'MeningitisCA',
#  'Anya_Nori', 'pharmamafia', 'CFragilite', 'EpiRen', 'NAV_igator', 'dey_aditi', 'NaTHNaC', 'ConPediatriaSLP', 'JoTrust',
#  'HenningTveit', 'filiamd']

# with open("Pulled_Exclude.json", 'w+') as f:
#     f.write(json.dumps(Retrieved))
#
# fileX = open("WHO_VSN_Members.json", 'r')
# for line in fileX:
#     test = json.loads(line)
# WHO_VSN_IDlist=list()
# for u in test:
#     WHO_VSN_IDlist.append(u["ID"])
#
# with open("Pulled_Exclude_IDs.json", 'w+') as f:
#     f.write(json.dumps(WHO_VSN_IDlist))
