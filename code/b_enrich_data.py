import pandas as pd, json
import numpy as np
from ast import literal_eval #pour gérer les colonnes qui contiennent des données en list

year = "[2018 TO 2021]"


## ______0______ Collaps all year
## load datas and tables 
df_dump = pd.read_csv(f"../data/dump_{year}.csv",
    converters={
    # nettoyage sur selfArchiving_bool qui peut contenir des champs vides
    "selfArchiving_bool" : lambda x: True if x == "True" else False, 
    # language est une liste
    'language_s': literal_eval}
    )

match_domain = json.load(open("../data/match_domains.json"))
group_publisher = json.load(open("../data/group_publishers.json"))
print("df size", len(df_dump))


# ______1______ deduce discipline
print(f"\n\nDeduce discipline\n-----------\n")
def deduce_discipline(row) : 

    # __a verify NA
    if pd.isna(row["primaryDomain_s"]) : 
        return pd.NA
    
    # __b normer le primary domain

    # nombre de . dans primary domain
    nb_point = row["primaryDomain_s"].count(".")
    if nb_point > 1 :
        # reduire à un seul point/division
        cut = row["primaryDomain_s"].split(".")
        prim_domain_cooked = ".".join([cut[0], cut[1]])
    else :
        prim_domain_cooked = row["primaryDomain_s"]

    # __c regarder si le primary domain normé est dans le matcher
    if prim_domain_cooked in match_domain.keys() : 
        return match_domain[prim_domain_cooked]
    # si non faire le matching avec le domaine parent seul
    else :
        # si cest un domaine de nivau premier absent du matching
        if prim_domain_cooked.count(".") == 0 : 
            print("domaine primaire absent du matching\t", prim_domain_cooked)
            return pd.NA

        # sil sagit dun domaine avec subdivision alors on match sur le parent seul
        else :
            # si le domaine parent nest pas dans le matching eg optique
            if prim_domain_cooked[:prim_domain_cooked.index(".")] not in match_domain.keys() : 
                print("domaine primaire absent du matching\t", prim_domain_cooked)
                return pd.NA

            return match_domain[prim_domain_cooked[:prim_domain_cooked.index(".")]]


df_dump["discipline"] = df_dump.apply(lambda row : deduce_discipline(row) , axis = 1)

# retrait des publications sans disciplines
df_dump.dropna(subset=['discipline'], inplace = True)

# print(df_dump["discipline"].value_counts())



# ______2______ deduce publisher
print(f"\n\nDeduce publisher\n-----------\n\n")

# du fait des doctype les publishers sont éclatées entre journalPublisher & publisher_s

# __a nettoyer colonne publisher_s

## publisher_s est une liste mais comprise comme une string
# retrait des apostrophes, des crochets
df_dump["publisher_s"] = df_dump["publisher_s"].str.replace("'","").str.strip("[]")
# couper à la virgule, sélectionner 1er publisher only
df_dump["publisher_s"] = df_dump["publisher_s"].str.split(',').str[0]
#print(len(df_dump["publisher_s"].value_counts()))

# __b déduire publisher : journalPublisher si non vide, sinon publisher_s 

df_dump["publisher"] = np.where(
    df_dump["journalPublisher_s"].isna(), df_dump["publisher_s"], df_dump["journalPublisher_s"]
    ) 

# __c group publisher names
 
## preparer le nettoyage
# minuscule
df_dump["publisher"] = df_dump["publisher"].str.lower()
# retrait carac spéciaux
import unidecode
def remove_spe_char(val) :
    # si la valeur est bien de type str
    if isinstance(val, str) :  
        return unidecode.unidecode(val)

df_dump["publisher"] = df_dump["publisher"].apply(lambda val : remove_spe_char(val))

# appliquer le groupement
df_dump["publisher"].replace(group_publisher, inplace = True)

print("nb de publisher", len(df_dump["publisher"].value_counts()))

#pour imprimer les n premiers publishers
print(df_dump["publisher"].value_counts()[:60]) 

# pour imprimer tous les publisher avec qtté de publication
# for col, val in df_dump["publisher"].value_counts().iteritems() : 
#     if val > 10 : 
#         print(col, '\t', val)


## ______n______ nettoyer la colonne language
print(f"\n\nClean language\n-----------\n\n")

# language_s est de type objet, c'est une liste
# créer nouvelle colonne language qui retient le premier de la liste dans language_s

df_dump["language"] = df_dump.language_s.apply(lambda x: x[0])

# print(
#     df_dump["new_col"].value_counts()
#     )



## ______n______ add wos scopus  doaj visibility
print("\n\nwos scopus doaj visibility\n-----------\n\n")

def concat_issns_from_df(df, pissn, eissn) : 
    """
    get all issn from a contains a col for pissn and eissn 
    pissn is the name for print issn column
    """
    p_issn = df[pissn][ df[pissn].notna()].to_list()
    e_issn = df[eissn][ df[eissn].notna()].to_list()
    return p_issn + e_issn


# Scopus assembles les ISSNs
scopus = pd.read_csv("../data/scopus-ext_list_March_2022.csv" , usecols = ["Print-ISSN", "E-ISSN"])
scopus_issn = concat_issns_from_df(scopus, "Print-ISSN", "E-ISSN")
print(f"scopus nb issn", len(scopus_issn))


# WOS assembler les ISSN
# le wos donne un fichier par sollection, il faut les assember
fn = ["wos-core_AHCI 2022-April-19", "wos-core_ESCI 2022-April-19", "wos-core_SCIE 2022-April-19", "wos-core_SSCI 2022-April-19"]
buffer = []
for name in fn :
    df = pd.read_csv("../data/wos/"+name + ".csv", usecols = ["ISSN", "eISSN"])
    buffer.append(df)

wos = pd.concat(buffer)
wos_issn = concat_issns_from_df(wos, "ISSN", "eISSN")
print(f"wos nb issn", len(wos_issn))

# DOAJ assembler les ISSN
doaj = pd.read_csv("../data/journalcsv__doaj_20220429_0736_utf8.csv", usecols=["Journal ISSN (print version)", "Journal EISSN (online version)"])
doaj_issn = concat_issns_from_df(doaj,"Journal ISSN (print version)", "Journal EISSN (online version)")
print(f"doaj nb issn", len(doaj_issn))

# faire les matching
df_dump["wos_scopus"] = np.where(
    (df_dump["journalIssn_s"].isin(scopus_issn + wos_issn)) | (df_dump["journalEissn_s"].isin(scopus_issn + wos_issn)),
    True,
    False)

df_dump["doaj"] = np.where(
    (df_dump["journalIssn_s"].isin(doaj_issn)) | (df_dump["journalEissn_s"].isin(doaj_issn)),
    True,
    False)


print(
    "nb publication in wos or scopus", len(df_dump[ df_dump["wos_scopus"]]),
    "\nnb publication in doaj", len(df_dump[ df_dump["doaj"]])
    )


# ______fin______ exporter
# retirer colonne brutes : publisher_s et languages_s
df_dump.drop(['publisher_s', "journalPublisher_s", "language_s"], axis = 1, inplace = True)
df_dump.to_csv(f"../data/enriched_data_{year}.csv", index = False)
print("------------\n\nfichier exporté")
