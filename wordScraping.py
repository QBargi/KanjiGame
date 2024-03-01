import requests
from bs4 import BeautifulSoup
import pyodbc


#CONNEXION TO THE DATABASE
conn_str = ("Driver={SQL Server};"
            "Server=LAPTOP-A8LPU60E\\SQLEXPRESS;"
            "Database=JEUKANJI;"
            "Trusted_Connection=yes;")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def is_kana(c):
    return u'\u3040' <= c <= u'\u30FF'

def wordScrapping(adresse):
    array=[]
    response=requests.get(adresse)
    soup=BeautifulSoup(response.content,"html.parser")
    scrap=soup.find_all("tr",attrs={'class':"jl-row"})
    for balise in scrap:
        word_kanji=balise.find("a",attrs={'class':"jl-link jp"})
        word_kana=balise.find("p",attrs={'class':'mb-0 mt-2'})
        if not is_kana(word_kanji.get_text()):
            array.append([word_kanji.get_text(),word_kana.get_text()])
    return array


array_voc=wordScrapping("https://jlptsensei.com/jlpt-n5-vocabulary-list/")
[cursor.execute(f"INSERT INTO MOTS VALUES (N'{word_kanji}',N'{word_kana}',5)") for [word_kanji,word_kana] in array_voc]
# cursor.execute("SELECT * FROM MOTS")
# for row in cursor:
#     print(row)
cursor.commit()
