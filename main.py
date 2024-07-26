import pyodbc #DATABASE LIBRARY
import random
import tkinter as Tk
from tkinter import ttk
import tkinter.font as tkFont


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
    cursor.execute("WITH MOTS_RN AS (\
                                SELECT ROW_NUMBER() OVER (ORDER BY MOT) RN,\
                                    MOT,\
                                    LECTURE\
                                FROM MOTS\
                                )\
                                SELECT * FROM MOTS_RN WHERE RN = CEILING(RAND()* (SELECT COUNT(*) FROM MOTS_RN))")
    return cursor.fetchone()

#RANDOM PICK OF A READING FOR THE KANJI kanji
def lecture_random(kanji):
    if is_kana(kanji): #CHECK IF THE CHARACTER kanji IS AN ALPHABET CHARACTER (KANA) OR A KANJI
        return kanji
    else:
        #WITH THE TABLE OF ALL THE LECTURES OF A KANJI, PICK A RANDOM LECTURE
        cursor.execute(f"WITH LECTURES_KANJI AS (\
                                SELECT ROW_NUMBER() OVER (ORDER BY LECTURE) RN,\
                                    ID,\
                                    LECTURE\
                                FROM KANJIS\
                                WHERE ID = N'{kanji}'\
                                )\
                        SELECT * FROM LECTURES_KANJI WHERE RN = CEILING(RAND()* (SELECT COUNT(*) FROM LECTURES_KANJI))")
        random_reading = cursor.fetchone()[2] #Select only the random-choosed lecture
        if not is_katakana(random_reading[0]): #Check if the reading is not in katakana, if it is, convert it to hiragana
            return random_reading
        else:
            random_reading_hiragana = ''
            for character in random_reading:
                random_reading_hiragana += katakana_to_hiragana(character)
            return random_reading_hiragana

#ASKING THE PLAYER AN ANSWER
def asking(possibilities):
    for i in range(len(possibilities)):
        print(f'{i+1} : {possibilities[i]}') #From 1 to 4
    print('-----------------------------')
    answer = ''
    while answer not in ['1','2','3','4']:
        answer = input("Insérez votre réponse: ")
    return int(answer)-1 #From 0 to 3

#RETURN AN ARRAY OF 4 POSSIBLES READINGS FOR word AND THE POSITION OF THE CORRECT READING IN THIS ARRAY
def array_possibilities(word):
    possibilities = ['-','-','-','-']
    position_result = random.randint(0,3)
    possibilities[position_result] = word[2]
    #Creation of 3 random possibilities
    for pos_new_lect in range(len(possibilities)):
        if pos_new_lect != position_result:
            new_lecture_random = ''
            while new_lecture_random not in possibilities:
                for kanji in word[1]:
                    if is_same_kanji(kanji): #CHECK IF THE CHARACTER kanji IS 々, THEN IT IS READ THE SAME WAY AS THE PREVIOUS ONE
                        new_lecture_random += new_lecture_character    
                    else:
                        new_lecture_character = lecture_random(kanji)
                        new_lecture_random += new_lecture_character
                if new_lecture_random not in possibilities: #We do not show a result twice 
                    possibilities[pos_new_lect] = new_lecture_random
                    break
                else: #If the new_lecture_random is already in the array, change a random kanji of the word by one from the same difficulty to get another reading
                    new_lecture_random = '' #To make the while loop again
                    while True:
                        random_change = random.randint(0,len(word[1])-1)
                        if not is_kana(word[1][random_change]) and not is_same_kanji(word[1][random_change]):
                            cursor.execute(f"WITH KANJI_RN AS (\
                                                                SELECT ROW_NUMBER() OVER (ORDER BY ID) RN,\
                                                                        ID,\
                                                                        LECTURE\
                                                                FROM KANJIS\
                                                                )\
                                                                SELECT * FROM KANJI_RN WHERE RN = CEILING(RAND()* (SELECT COUNT(*) FROM KANJI_RN))")
                            random_change_kanji = cursor.fetchone()[1]
                            word[1] = word[1].replace(word[1][random_change],random_change_kanji) #Il faut mettre un kanji random ici
                            break
    return [possibilities, position_result]

#RETURN TRUE IF c IS A KANA (ONE OF THE JAPANESE ALPHABET)
def is_kana(c):
    return u'\u3040' <= c <= u'\u30FF'

#RETURN TRUE IF c IS A KATAKANA (ONE OF THE JAPANESE ALPHABET)
def is_katakana(c):
    return u'\u30A0' <= c <= u'\u30FF'

def is_same_kanji(c):
    return c == "々"

#CONVERT A KATAKANA CHARACTER TO A HIRAGANA CHARACTER USING UNICODE
def katakana_to_hiragana(c):
    return chr(ord(c)-0x0060)

def jeu():
    print("--- Bienvenue dans le jeu des kanjis ---\n")
    result = pick_a_word()
    print(f'Comment se lit le mot {result[1]}?') #result[1] is the word in kanjis
    possibilities,position_result = array_possibilities(result)
    if asking(possibilities) == position_result:
        print("Félicitations!")
    else:
        print(f"Dommage... La bonne réponse était {result[2]}")


def app():
    #CREATION OF THE APP
    root = Tk.Tk()
    frm = ttk.Frame(root,padding=10)
    frm.grid()
    fontObj = tkFont.Font(size=18)

    #CREATION OF THE FIRST ROUND OF THE GAME
    result = pick_a_word()
    possibilities,position_result = array_possibilities(result)

    ttk.Label(frm, text=f"Comment se lit le mot suivant: {result[1]}?", font=fontObj).grid(column=0, row=0)
    for i in range(len(possibilities)):
        button = Tk.Button(frm, text=possibilities[i], command= lambda text=possibilities[i]: print(text), font=fontObj).grid(column=0, row=i+1)
    button = Tk.Button(frm, text="Quit", command= root.destroy, font=fontObj).grid(column=0, row=7)
    root.mainloop()

app()

# jeu()