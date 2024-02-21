import pyodbc #DATABASE LIBRARY
import random


#CONNEXION TO THE DATABASE
conn_str = ("Driver={SQL Server};"
            "Server=LAPTOP-A8LPU60E\SQLEXPRESS;"
            "Database=JEUKANJI;"
            "Trusted_Connection=yes;")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

#FIRST INSTRUCTION TO THE DATABASE
#cursor.execute("SELECT * FROM KANJIS")
#for row in cursor:
#    print(row)

#RANDOM PICK OF A WORD
def pick_a_word():
    cursor.execute("SELECT * FROM MOTS WHERE ID = FLOOR(RAND()* (SELECT MAX(ID) FROM MOTS))+1")
    return cursor.fetchone()

#RANDOM PICK OF A LECTURE
def lecture_random(kanji):
    #WITH THE TABLE OF ALL THE LECTURES OF A KANJI, PICK A RANDOM LECTURE
    cursor.execute(f"WITH LECTURES_KANJI AS (\
                            SELECT ROW_NUMBER() OVER (PARTITION BY ID ORDER BY LECTURE) RN,\
                                   ID,\
                                   LECTURE\
                            FROM KANJIS\
                            WHERE ID=N'{kanji}'\
                            )\
                     SELECT * FROM LECTURES_KANJI WHERE RN = FLOOR(RAND()* (SELECT MAX(RN) FROM LECTURES_KANJI))+1")
    return cursor.fetchone()[2] #Return only the random-choosed lecture

#Affichage
def affichage(possibilities):
    for i in range(len(possibilities)):
        print(f'{i+1} : {possibilities[i]}') #From 1 to 4
    print('-----------------------------')
    answer=''
    while answer not in ['1','2','3','4']:
        answer=input("Insérez votre réponse: ")
    return int(answer)-1 #From 0 to 3

def is_kana(c):
    return u'\u3040' <= c <= u'\u30FF'

def jeu():
    print("--- Bienvenue dans le jeu des kanjis ---\n")
    result=pick_a_word()
    print(f'Comment se lit le mot {result[1]}?') #result[1] is the word in kanjis
    possibilities=['','','','']
    position_result=random.randint(0,3)
    possibilities[position_result]=result[2]
    #Creation of 3 random lectures
    for pos_new_lect in range(len(possibilities)):
        if pos_new_lect!=position_result:
            while True:
                new_lecture_random=''
                for kanji in result[1]:
                    new_lecture_random+=lecture_random(kanji)
                if new_lecture_random!=result[2]: #We do not show the good result twice --- NEED TO CHECK THERE ARE NOT 2 SAME ANSWERS
                    break 
            possibilities[pos_new_lect]=new_lecture_random
    if affichage(possibilities)==position_result:
        print("Félicitations!")
    else:
        print("Dommage...")


#print(is_kana("々"))
jeu()