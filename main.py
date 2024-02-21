import pyodbc #DATABASE LIBRARY
import random


#CONNEXION TO THE DATABASE
conn_str = ("Driver={SQL Server};"
            "Server=LAPTOP-A8LPU60E\\SQLEXPRESS;"
            "Database=JEUKANJI;"
            "Trusted_Connection=yes;")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


#RANDOM PICK OF A WORD
#RETURN AN ARRAY CONTAINING THE INFORMATION OF THE WORD LIKE [ID, KANJIS, LECTURE]
def pick_a_word():
    cursor.execute("SELECT * FROM MOTS WHERE ID = FLOOR(RAND()* (SELECT MAX(ID) FROM MOTS))+1")
    return cursor.fetchone()

#RANDOM PICK OF A READING FOR THE KANJI kanji
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
    random_reading=cursor.fetchone()[2] #Select only the random-choosed lecture
    if not is_katakana(random_reading[0]): #Check if the reading is not in katakana, if it is, convert it to hiragana
        return random_reading
    else:
        random_reading_hiragana=''
        for caracter in random_reading:
            random_reading_hiragana+=katakana_to_hiragana(caracter)
        return random_reading_hiragana

#ASKING THE PLAYER AN ANSWER
def asking(possibilities):
    for i in range(len(possibilities)):
        print(f'{i+1} : {possibilities[i]}') #From 1 to 4
    print('-----------------------------')
    answer=''
    while answer not in ['1','2','3','4']:
        answer=input("Insérez votre réponse: ")
    return int(answer)-1 #From 0 to 3

#RETURN AN ARRAY OF 4 POSSIBLES READINGS FOR word AND THE POSITION OF THE CORRECT READING IN THIS ARRAY
def array_possibilities(word):
    possibilities=['','','','']
    position_result=random.randint(0,3)
    possibilities[position_result]=word[2]
    #Creation of 3 random possibilities
    for pos_new_lect in range(len(possibilities)):
        if pos_new_lect!=position_result:
            while True:
                new_lecture_random=''
                for kanji in word[1]:
                    new_lecture_random+=lecture_random(kanji)
                if new_lecture_random!=word[2]: #We do not show the good result twice --- NEED TO CHECK THERE ARE NOT 2 SAME ANSWERS
                    break 
            possibilities[pos_new_lect]=new_lecture_random
    return [possibilities, position_result]

#RETURN TRUE IF c IS A KANA (ONE OF THE JAPANESE ALPHABET)
def is_kana(c):
    return u'\u3040' <= c <= u'\u30FF'

#RETURN TRUE IF c IS A KATAKANA (ONE OF THE JAPANESE ALPHABET)
def is_katakana(c):
    return u'\u30A0' <= c <= u'\u30FF'

#CONVERT A KATAKANA CARACTER TO A HIRAGANA CARACTER USING UNICODE
def katakana_to_hiragana(c):
    return chr(ord(c)-0x0060)

def jeu():
    print("--- Bienvenue dans le jeu des kanjis ---\n")
    result=pick_a_word()
    print(f'Comment se lit le mot {result[1]}?') #result[1] is the word in kanjis
    possibilities,position_result=array_possibilities(result)
    if asking(possibilities)==position_result:
        print("Félicitations!")
    else:
        print("Dommage...")


#print(is_kana("々")) #Faut régler ce pb
jeu()