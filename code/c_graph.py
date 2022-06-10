import pandas as pd, matplotlib, matplotlib.pyplot  as plt
import numpy as np

file_name = "enriched_data_[2018 TO 2021].csv"
df = pd.read_csv(f"../data/{file_name}")

print( "taille df", len(df))

"""
memo sur les publishers
bmc gardé à bmc, à remplacer par springer nature pour calcul de diversité
"""


def horiz_hist_remove_axis() : 
    """
    configure horizontal graph : remove axis
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # retirer l'origine sur Y
    yticks = ax.yaxis.get_major_ticks()
    yticks[0].label1.set_visible(False)


def horiz_hist_add_labels(df, column, x_shift):
    """
    ajout des labales sur le haut des histogrammes
    """
    #iteration numérique
    for iterator in range(len(df.index)) :
        ax.annotate(
            round( df.at[ df.index.tolist()[iterator], column] ),
            # position xy
            xy = (
                iterator + x_shift,
                df.at[ df.index.tolist()[iterator], column] 
                ),
            xytext = (0, 8), 
            size = 7, 
            textcoords="offset points",
            ha='center', 
            va='bottom',
            color='grey')

#_____________________________________________
## graph open access & HAL indicators
print(f"\n\nopen access & hal")

# print(
#     len(
#         df[ (df["submitType_s"] == "file") ] # & (df["selfArchiving_bool"] == True)
#     ) / len(df)
#     )

# ___a déduire les colonnes
# avec fichier et déposé par l'auteur
df["hal_file"] = np.where(
    df["submitType_s"] == "file",
    True,
    False
    )

# idée : ? prendre en compte les notices déposées par l'auteur et en open access arXiv

# avec fichier non self archiving
df["hal_self_archiving"] = np.where(
    (df["submitType_s"] == "file") & (df["selfArchiving_bool"] == True),
    True,
    False
    )
# print(df["self_archiving"].value_counts())

# ___b repartir par disciplines
dfhal = pd.DataFrame(df.groupby(["discipline"])
    [["openAccess_bool", "hal_file", "hal_self_archiving"]].agg(["count", "mean"])
    )

# multiplier par 100
dfhal = dfhal.mul(100)
dfhal.columns = ["nb","openAccess_bool", "nb2", "hal_file", "nb3", "hal_self_archiving" ]
discipline = np.arange(len(dfhal.index))


# ___c alimenter graph

width = 0.15

fig, (ax) = plt.subplots(figsize=(14,10), dpi = 100, facecolor = 'w', edgecolor = 'k')

ax.bar( discipline - width - 0.05, dfhal.openAccess_bool, width, label= "Open Access", color = "#2a9d8f")
ax.bar( discipline , dfhal.hal_file, width, label= "HAL file", color = "#e9c46a")
ax.bar( discipline + width + 0.05, dfhal.hal_self_archiving, width, label= "HAL file self archving", color = "#f4a261")


# ___d configurer l'affichage
horiz_hist_remove_axis()

# tracer les grilles 
ax.yaxis.grid(ls='--', alpha=0.2)
# premier arg les ticks, 2e les labels
plt.yticks(np.arange(0, 110, step=20), [str(val) + "%" for val in range(0, 110, 20)], fontsize = 10)

# x axis afficher les disciplines
ax.set_xticks(discipline)
# afficher uniquement le premier terme du nom complet de la discipline
ax.set_xticklabels([n.split()[0] for n in dfhal.index], fontsize = 11)

# ajouter label
horiz_hist_add_labels(dfhal, "openAccess_bool", - width - 0.05)
horiz_hist_add_labels(dfhal, "hal_file", 0)
horiz_hist_add_labels(dfhal, "hal_self_archiving", width + 0.05)

plt.legend( 
    frameon = True, markerscale = 1, loc = "center", ncol = 3, bbox_to_anchor=(0.5, 1.02), framealpha= False
    )
ax.set_title("Open Access & HAL", fontsize=16, alpha = 0.6, y = 1.05)
plt.savefig("../img/open-access-hal.png", dpi=100, bbox_inches='tight')


# plt.show()
# exit()






#_____________________________________________
## graph visibility


## pour réduire aux docType avec ISSN, les articles 
# df = df[ df["docType_s"] == "ART"].copy()

# ___a repartir has_doi, wos_scopus, doaj par disicpline
df["has_doi"] = df["doiId_s"].notna()
# print(df.has_doi.value_counts())

dfviz = pd.DataFrame(df.groupby(["discipline"])
[["has_doi", "wos_scopus", "doaj"]].agg(['mean']))
# passer du mean au pourcentage
dfviz = dfviz.mul(100)

#renomer les colonnes (en sortie du groupby on est sur deux niveau : réduction à un seul)
dfviz.columns = ["has_doi_mean", "in_wos_scopus_mean", "in_doaj_mean"]
discipline = np.arange(len(dfviz.index))
#print(dfviz)

# ___b graph
width = 0.15

fig, (ax) = plt.subplots(figsize=(14,10), dpi = 100, facecolor = 'w', edgecolor = 'k')

ax.bar( discipline - width/2 - 0.01, dfviz.has_doi_mean, width, label= "has DOI", color = "#eceff1")
ax.bar( discipline + width /2, dfviz.in_wos_scopus_mean, width, label= "in Wos or Scopus", color = "#4fc3f7")
# ax.bar( discipline + width + 0.01, dfviz.in_doaj_mean, width, label= "in DOAJ", color = "#ffcc80")


# ___c configurer l'affichage
horiz_hist_remove_axis()

# tracer les grilles 
ax.yaxis.grid(ls='--', alpha=0.1)
plt.yticks([i for i in range(0, 120, 20)], fontsize = 10)

# afficher les disciplines
ax.set_xticks(discipline)
ax.set_xticklabels([n.split()[0] for n in dfviz.index], fontsize = 11)

# ajouter les labels
horiz_hist_add_labels(dfviz, "has_doi_mean", - width/2 - 0.01)
horiz_hist_add_labels(dfviz, "in_wos_scopus_mean", width/2)


plt.legend( 
    frameon = True, markerscale = 1, loc = "center", ncol = 3, bbox_to_anchor=(0.5, 1.02), framealpha= False  )
ax.set_title("Discipline visibility", fontsize=16, alpha = 0.6, y = 1.05)
plt.savefig("../img/discipline-visibility.png", dpi=100, bbox_inches='tight')
print("discipline-visibility.png\t saved")
#plt.show()

#exit()



## ___________________
# fonction pour les hist horizontaux


def remove_axis(ax) : 
    """
    retire l'absicce et les ticks
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # remove xticks
    plt.tick_params(
      axis='x',          # changes apply to the x-axis
      which='both',      # both major and minor ticks are affected
      bottom=False,      # ticks along the bottom edge are off
      labelbottom=False) # labels along the bottom edge are off


def add_labels(df, ax, min_width) : 
    """
    ajout des valeurs de pourcentage
    df, la df
    ax,  le graph
    min_width : valeur au dessus de laquelle ajouter les labels
    """

    labels = []
    for j in df.columns:
      for i in df.index:
          label = df.loc[i][j]
          if not isinstance(label, str) : 
            #pour un meilleur affichage : s'assurer que ce n'est pas la discipline et alors arrondir
            label = str(round(label))
            label += " %"     #:label.find(".")
            labels.append(label)          

    patches = ax.patches
    for label, rect in zip(labels, patches):
        width = rect.get_width()
        # mettre le label unquement si la largeur est sup. à min_width
        if width > min_width :
            x = rect.get_x()
            y = rect.get_y()
            height = rect.get_height()
            ax.text(x + width/2., y + height/2., label, ha='center', va='center', fontsize = 8)






#_____________________________________________
## graph doctype


# print(df.docType_s.value_counts())


# __a cross tab
doctype = pd.crosstab(df["discipline"], df["docType_s"])
# passer en pourcentage 
doctype = doctype.T
doctype = doctype / doctype.sum() * 100
doctype = doctype.T
doctype.sort_index(ascending = False, inplace = True)


# __b load graphic
ax = doctype.plot(kind = "barh", 
stacked=True, 
figsize=(14, 10),
 color = ["#9dd866", "#6f4e7c", "#0b84a5", "grey", "#ffa056", "#f6c85f"]
 )

remove_axis(ax)

add_labels(doctype, ax, 3)

plt.ylabel(None, fontsize = 15)
plt.legend( 
    frameon = True, markerscale = 1, loc = "center", ncol = 3, bbox_to_anchor=(0.5, 1.02), framealpha= False  )
plt.title("Publication type diversity", fontsize = 25, x = 0.49, y = 1.07,  alpha = 0.6)
plt.savefig("../img/publication-type-diversity.png", dpi=100, bbox_inches='tight')
print("publication-type-diversity.png\t saved")
#plt.show()




#_____________________________________________
## graph language
print(f"\n\n langauge diversity")


# ___a preparer les données
# on retient les 4 premiers langues, les autres sont regroupées dans other

# print(df["language"].value_counts())

# repartition des langages par quantité
all_language =  df["language"].value_counts()
#print(type(all_language))
# print(all_language.index)

#retenir que les 4 premiers : all_language.index[:4]

def add_other(value) : 
    """
    retenir uniquement les 4 premières langues, ensuite "other"
    """
    if value not in all_language.index[:4] : 
        return "other"
    else :
        return value

df["language"] = df["language"].apply(lambda value : add_other(value))

# ___b tab croisé
lang = pd.crosstab(df["discipline"], df["language"]) 
# passer en pourcentage
lang = lang.T
lang = lang / lang.sum() * 100
lang = lang.T
lang.sort_index(ascending = False, inplace = True)

# ___c alimenter l'affichage
ax = lang.plot(kind = "barh", 
stacked=True, 
figsize=(14, 10),
 color = ["#9dd866", "#6f4e7c", "#0b84a5", "grey", "#ffa056", "#f6c85f"]
 )

remove_axis(ax)

add_labels(lang, ax, 3)

plt.ylabel(None, fontsize = 15)
plt.legend( 
    frameon = True, markerscale = 1, loc = "center", ncol = 3, bbox_to_anchor=(0.5, 1.02), framealpha= False  )
plt.title("Language diversity", fontsize = 25, x = 0.49, y = 1.07,  alpha = 0.6)
plt.savefig("../img/language-diversity.png", dpi=100, bbox_inches='tight')
print("language-diversity.png\t saved")
#plt.show()



# exit()




#_____________________________________________
## graph Oligopolistic dependency

## __a enrichir les données : faire la typologie de publisher
pub_type = {
"oligopoly" : ["elsevier", "springer nature", "wiley", "american physical society", "taylor & francis", "sage publications"],
"OAcommercial" : ["frontiers", "mdpi", "iop publishing", "hindawi", "bmc"]
}
# print(df["publisher"].value_counts()[:20])


def deduce_publisher_type(pub) : 
    """
    3 type de publisher : olygopole, OA commercial et other
    """
    if pub in pub_type["oligopoly"] : 
        return "1.oligopoly"

    elif pub in pub_type["OAcommercial"] : 
        return "2.OAcommercial"
    else : 
        return "3.other"


df["pub_type"] = df["publisher"].apply(lambda x : deduce_publisher_type(x))

# print(df.pub_type.value_counts())

# ___b tab croisé
pubtype = pd.crosstab(df["discipline"], df["pub_type"]) 
# passer en pourcentage
pubtype = pubtype.T
pubtype = pubtype / pubtype.sum() * 100
pubtype = pubtype.T
pubtype.sort_index(ascending = False, inplace = True)

# print(pubtype.columns)

# ___c alimenter l'affichage
ax = pubtype.plot(kind = "barh", 
stacked=True, 
figsize=(14, 10),
 color = ["#ab47bc", "#e1bee7", "#e0e0e0"]
 )

remove_axis(ax)

add_labels(pubtype, ax, 5)


plt.ylabel(None, fontsize = 15)
plt.legend( ["oligopoly", "OAcommercial", "other"],
    frameon = True, markerscale = 1, loc = "center", ncol = 3, bbox_to_anchor=(0.5, 1.02), framealpha= False  )
plt.title("Oligopolistic dependency", fontsize = 25, x = 0.49, y = 1.07,  alpha = 0.6)
plt.savefig("../img/oligopoly-dependency.png", dpi=100, bbox_inches='tight')
print("oligopoly-dependency.png\t saved")
