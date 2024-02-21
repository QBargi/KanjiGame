import requests
from bs4 import BeautifulSoup
import re
import pyodbc

#CONNEXION TO THE DATABASE
conn_str = ("Driver={SQL Server};"
            "Server=LAPTOP-A8LPU60E\SQLEXPRESS;"
            "Database=JEUKANJI;"
            "Trusted_Connection=yes;")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

#Scrapping du kanji décrit à l'url adresse
def kanji_scraping(adresse):
    response=requests.get(adresse)
    soup=BeautifulSoup(response.content,"html.parser")
    kanji=str(soup.title)[19]
    print("Kanji selectionné: ",kanji) #KANJI
    scrap_readings=soup.find_all('span',attrs={'class':"kt_text"}) #On récupère les lectures ON et KUN (2 balises)
    #print("Différentes lectures:")
    for balise in scrap_readings: 
        scrap_balise=re.split('\(|\)',str(balise)) #On isole la lecture dans la balise
        i=1
        while i<len(scrap_balise):
            if '-' not in scrap_balise[i]: #On vérifie que la lecture est la lecture du kanji SEUL (sans kana à coté)
                #print(scrap_balise[i]) #LECTURE
                cursor.execute(f"INSERT INTO KANJIS VALUES (N'{kanji}',N'{scrap_balise[i]}')")
            i+=2
    balise_difficulty=soup.find('ul',attrs={'class':"tag"})
    difficulty=str(balise_difficulty).split("Level ")[1].rsplit("<")[0] #On récupère uniquement le niveau
    #print("Difficulté:",difficulty) #DIFFICULTY
    cursor.execute(f"INSERT INTO DIFFICULTIES VALUES (N'{kanji}','{difficulty}')")
    
#Scrapping des urls de kanji sur la page d'accueil du dictionnaire des joyo kanjis (https://jitenon.com/cat/common_kanji.php)
#Renvoie un tableau des urls des kanjis comportant nb_strokes traits
def url_scraping(nb_strokes):
    response=requests.get("https://jitenon.com/cat/common_kanji.php")
    soup=BeautifulSoup(response.content,"html.parser")
    kanjiByStroke=soup.find("div",attrs={'id':f'parts{nb_strokes}'})
    return ["https:"+link.get('href') for link in kanjiByStroke.find_all('a')]

for nb_strokes in range(1,24): #Scrapping des kanjis comportant de 1 à 24 traits
    for link in url_scraping(nb_strokes):
        kanji_scraping(link)
kanji_scraping("https://jitenon.com/kanji/%E9%AC%B1") #Scrapping du kanji manquant (29 traits)
cursor.commit()