import requests
from bs4 import BeautifulSoup
from settings import *
from unidecode import unidecode
from colorama import Fore

url = "https://www.axl.cefan.ulaval.ca/europe/france_departements.htm"
request = requests.get(url)
soup = BeautifulSoup(request.content, "html.parser")
listeimport = soup.find_all("table")
listeimport2 = listeimport[2]
soup_listeimport2 = BeautifulSoup(str(listeimport2), "html.parser")
listeimporttr = soup_listeimport2.find_all("tr")
dict_import_dep = []
for i,row in enumerate(listeimporttr):
    if i != 0:
        lignes = row.find_all("td")
        num_dep = lignes[0].text.strip()
        nom_dep = lignes[1].text.strip()
        nom_dep = nom_dep.lower()
        nom_dep = unidecode(nom_dep)
        nom_dep = nom_dep.replace(" ","-")
        dict_import_dep.append({num_dep:nom_dep})

CP2 = CODE_POSTAL[:2]
for row in dict_import_dep:
    if CP2 in row:
        Departement = (row.get(CP2))

url = f"https://prix-carburants-info.fr/departements/{Departement}.html"
request = requests.get(url)
soup = BeautifulSoup(request.content, "html.parser")
stations = soup.find_all("div", class_="bindpopup")
soup = BeautifulSoup(request.content, "html.parser")
prices = soup.find_all("td", class_="col-2")
dict_prix = []
prix = []
count = 0
deleteindic = 0
for row in prices:
    row = row.get_text()
    row = row.replace("-", "Pas de prix")
    prix.append(row)
    count += 1
    if count == 6:
        if deleteindic % 2 == 1:
            dict_prix.append(prix)
            prix = []
            count = 0
        else:
            prix = []
            count = 0
        deleteindic += 1
i = 0
stations_liste = []
dates = ["aujourd'hui","hier","avant-hier"]
for i,station in enumerate(stations):
    station_name = station.find("a").text.strip()
    station_address = station.find_next_sibling("div").text.strip()
    station_address_road = station_address[:station_address.index(CODE_POSTAL[0:2])]
    station_address_CP = station_address[station_address.index(CODE_POSTAL[0:2]):]
    station_address_ville = station_address_CP[6:]
    station_address_CP = station_address_CP[:5]
    prix_info = station.find_next("div", class_="mt-2")
    prix_mise_a_jour = prix_info.find("span", class_="badge").text.strip()
    prix_carburants = prix_info.find_next_siblings("tr")
    j=0
    verifbool=False
    for j,date in enumerate(dates):
        if prix_mise_a_jour == date:
            prix_mise_a_jour_nb = j
            verifbool = True
    if verifbool==False:
        prix_maj = prix_mise_a_jour.split(" ")
        prix_mise_a_jour_nb = prix_maj[3]
    gazole = dict_prix[i][0]
    sp95 = dict_prix[i][1]
    e10 = dict_prix[i][2]
    sp98 = dict_prix[i][3]
    e85 = dict_prix[i][4]
    gpl = dict_prix[i][5]
    prix_carburant = [gazole,sp95,e10,sp98,e85,gpl]
    stations_liste.append({"Nom": station_name,
                           "Adresse":station_address_road,
                           "CP":station_address_CP,
                           "Ville":station_address_ville,
                           "Maj":prix_mise_a_jour,
                           "Majnb":prix_mise_a_jour_nb,
                           "Gazole":gazole,
                           "SP95":sp95,
                           "E10":e10,
                           "SP98":sp98,
                           "E85":e85,
                           "GPL":gpl})
moyennes = []
titre_carburant = ["Gazole","SP95","E10","SP98","E85","GPLc"]
for i in range(6):
    somme = 0
    compteur = 0
    for j in dict_prix:
        prix_carburant = j[i]
        prix_carburant = prix_carburant.replace("€","")
        prix_carburant = prix_carburant.replace(" ","")
        prix_carburant = prix_carburant.replace("Pasdeprix","")
        if prix_carburant == "":
            somme += 0
        else:
            prix_carburant = float(prix_carburant)
            somme += prix_carburant
            compteur+=1
    moyenne = somme / compteur
    moyennes.append({titre_carburant[i]:"{:.3f}".format(moyenne)})
station_liste_localisee = []
for row in stations_liste:
    CPV = CODE_POSTAL
    CP = row.get("CP")
    if CP == CPV:
        station_liste_localisee.append(row)
for row in station_liste_localisee:
    print(row.get("Nom"))
    print(row.get("Adresse"))
    print(row.get("Ville"))
    print(f"{CARBURANT}", row.get(CARBURANT))
    for i,rows in enumerate(moyennes):
        if CARBURANT in rows:
            prix_carburant = next((carburant.get(CARBURANT) for carburant in moyennes), None)
    difference = float(row.get(CARBURANT).replace(" €",""))-float(prix_carburant)

    if difference > 0:
        price = Fore.RED + "+" + str(round(difference,2)) + " €" + Fore.RESET
    else:
        price = Fore.GREEN + str(round(difference,2)) + " €" + Fore.RESET
    print("Différence",price)
    print(row.get('Maj'),'\n')