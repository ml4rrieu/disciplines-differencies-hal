import pandas as pd, requests, json



# anne de publication. possible d indiquer un intervalle [2018 TO 2021] 
year = "[2018 TO 2021]"


## ___0___ construct hal query
udice = "(UNIV-LYON1 OR UNIV-AMU OR UGA OR UNIV-BORDEAUX OR SORBONNE-UNIVERSITE OR PSL OR\
 UNIV-PARIS-SACLAY OR UNIV-COTEDAZUR OR UNIV-STRASBG OR UNIV-PARIS)"

doctype = "(ART OR COMM OR COUV OR UNDEFINED OR OUV OR DOUV)"

fields_cat = {
"global" : ["docid", "halId_s", "publicationDateY_i", "primaryDomain_s", "journalTitle_s", "journalDoiRoot_s", "conferenceTitle_s", "isbn_s", "bookTitle_s", "anrProjectId_i", "europeanProjectId_i", "funding_s"],
"diversity" : ["docType_s", "language_s", "journalPublisher_s", "publisher_s", "country_s"],
"monitoring" : ["doiId_s", "journalIssn_s", "journalEissn_s"],
"oa" : ["openAccess_bool", "linkExtId_s", "submitType_s", "licence_s"],
"hal" : ["submitType_s", "selfArchiving_bool", "researchData_s"]
}

# concaténer les métadonnées
fields = [* fields_cat["global"], *fields_cat["diversity"], *fields_cat["monitoring"], *fields_cat["oa"], *fields_cat["hal"]]

# si on souhaite reduire a UDICE
#q=collCode_s:{udice}&

# que les struct en fr ? structCountry_s:fr

# construire la requête HAL
hal_req = f"https://api.archives-ouvertes.fr/search/?\
fq=docType_s:{doctype}\
&fq=publicationDateY_i:{year}\
&fl={','.join(fields)}\
&rows=10000&sort=docid asc"

print(hal_req)

# nb de doc dientifié
req_total = requests.get( hal_req + "&rows=0").json()
pub_total = req_total["response"]["numFound"]
print("numFound : ", pub_total)


## ___1____ retrieve data from HAL API 

df_main = pd.DataFrame()

## utiliser le fonctionnement de curseur pour gd nombre de données
# cf. doc https://api.archives-ouvertes.fr/docs/search/?#rows

# loop management
loop = 0
end_reached = False
cursor_val = cursor_val_buffer = False

while not end_reached  : 
    loop += 1
    print("\nloop", loop)
    
    # first : cursor_val has no value
    if not cursor_val : 
        cursor_val = "*"
        query_hal = True

    # second : cursor_val is different than the one recolted
    elif cursor_val != cursor_val_buffer : 
        cursor_val = cursor_val_buffer
        query_hal = True

    # third : cursor_val is the same as the result
    elif cursor_val == cursor_val_buffer : 
        print("\tlast loop : no query hal")
        break
        query_hal = False
        end_reached = True

    if query_hal : 
        print(f"\tquery cursorval {cursor_val}")

        # placer le cursorMark en paramètre en dict pour requests 
        # cela evite des pbs d'encodage
        cursor_param = {"cursorMark" : cursor_val}

        r = requests.get( hal_req, params = cursor_param ).json()
        
        try : 
            r["response"]
            print("\tHAL API answer OK")
        except:
            print(f"\tHAL API no response key. HAL API Answer : \n\n\t{r}")
            exit()

        cursor_val_buffer = r["nextCursorMark"]
        print(f"\tcursorval result {cursor_val_buffer}")

        # recupérer les données
        hal_docs = r["response"]["docs"]
        df_temp = pd.json_normalize(hal_docs)
        df_main = pd.concat([df_main, df_temp], ignore_index = True)
        print(f"\ttaille df {len(df_main)}")



        

print("\n\ntaille df", len(df_main))
df_main.to_csv(f"../data/dump_{year}.csv", index = False)


