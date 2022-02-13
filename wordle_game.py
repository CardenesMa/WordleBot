#This program solves the wordle challenge
#Code Author: Kush Bandi

#Importing necessary modules

import pyautogui
import time
import wordl
import PIL.ImageGrab
from math import sqrt

#This function types an inputted word utilizing the pyautogui module
def type_word(word_to_type):
    k = wordl.Word(0, word_to_type)
    k.chars = word_to_type.split()

#This function helps get absolute colors (due to variations on the website)
def closest_color(list_of_colors, rgb):

    #Getting the r, g, and b values, and creating a color difference array
    r, g, b = rgb
    color_diffs = []

    #List_of_colors is an array containing grey, green, and yellow rgb values
    for color in list_of_colors:

        #Getting the specfic r, g, and b values of those colors
        cr, cg, cb = color

        #Setting the difference to the square root of the individual r, g, b differences squared
        color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)

        #Adding the difference to our array of differences
        color_diffs.append((color_diff, color))

    #Returning the smallest item as it represents the smallest difference
    return min(color_diffs)[1]

#This function eliminates words from wordList depening on colors of tiles
def find_next(info_arr, wordList):
	
    #Running this whole loop section several times due to python not parsing properly
    for i in range(6):

        #Looking at our informational array
        for x in info_arr:

            #If the color in our info_array is grey, we don't want any words that have that letter
            if x[1] == "grey":

                #The following for loop removes all words in wordList with that letter
                for word in wordList:

                    #However, we need to check if the letter exists and is green to ensure we don't accidentally remove words
                    letter_exists = False

                    #Going through the info_arr again to do the previous statement
                    for y in info_arr:

                        #If we encounter our current letter AND it has the green attribute, set the boolean to true
                        if (x[0] == y[0]) and (y[1] == 'green'):
                            letter_exists = True

                    #If the boolean is false and the grey letter is in a word, remove it
                    if x[0] in word and not letter_exists:
                            wordList.remove(word)

            #If the color in our info_array is green, we only want words that have that letter in that position
            elif x[1] == "green":

                #The following for loop removes all words in wordList that do not follow the condition above
                for word in wordList:
                    if not word[x[2]] == x[0]:
                        wordList.remove(word)

            #If the color is neither green nor grey, it is yellow, and we want to remove all words in wordList that do not contain this letter or have it in the same position
            else:

                #The following for loop removes all words that do not have this letter or have it in the same position
                for word in wordList:
                    if (x[0] not in word) or (x[0] == word[x[2]]):
                        wordList.remove(word)

    #Choosing the next word to type based on number of unique letters
    most_unique = 0
    best_word = ""
    unique_letters = []

    #We want to check the uniqueness of all words:
    for word in wordList:

        #The following for loop loops through a word and appends its letters to an array if they are unique relative ot the word itself
        unique_letters = []
        for x in word:
            if x not in unique_letters:
                unique_letters.append(x)

        #Then, to get the number of unique letters, simply get the length of the array
        num_unique = len(unique_letters)

        #Most_unique keeps track of the word with the most unique letters
        #If we get to a word with more unique letters, we set most_unique to num_unique and set the word to the best word variable
        if num_unique > most_unique:
            most_unique = num_unique
            best_word = word

    #Returning the best_word
    return best_word

#This function forms the informational array used universally throughout the code
def get_color_info(line_number, word, arr_of_info, check_completion, list_of_colors, positions, colors):

    #This loop goes through the word we have just typed
    # for x in range(len(word)):

    #     #This gets the rgb values of the squares in the current line, utilizes heavy variable math to determine where to look
    #     rgb = PIL.ImageGrab.grab().load()[positions[0] + (x*positions[2]), positions[1] + (line_number*positions[3])]

    #     #Utilizing the closest_color method to get our true rgb values instead of slightly-off rgb values
    #     true_rgb = closest_color(list_of_colors, rgb)

    #     #If the true_rgb values are grey...
    #     if true_rgb == list(colors[0]):

    #         #We add a tuple to arr_of_info which has the letter, the string "grey", and its position in the word
    #         arr_of_info.append((word[x], 'grey', x))

    #         #The importance of check completion is explained on line 156:
    #         #The only thing to note is that grey and yellow are set to False, and green is set to True
    #         check_completion.append(False)

    #     #If the true_rgb values are yellow...
    #     elif true_rgb == list(colors[1]):

    #         #We add a tuple to arr_of_info which has the letter, the string "yellow", and its position in the word
    #         arr_of_info.append((word[x], 'yellow', x))
    #         check_completion.append(False)

    #     #If both conditions above fail, it is green...
    #     else:

    #         #We add a tuple to arr_of_info which has the letter, the string "green", and its position in the word
    #         arr_of_info.append((word[x], 'green', x))
    #         check_completion.append(True)

    # #Finally, we return this array containing most information in this algorithm
    # return arr_of_info
    
    # inputs : (char, color, index)
    arr_of_info = []

    # word is going to be a Word type wordl
    for i in range(len(word.words)):
        letter = word.words[i]
        color = word.colors[i]
        arr_of_info.append(letter, color, i)

#This is the "master function" which utilizes all previous functions to actually solve the wordle live
def wordle_solver(wordList, position_arr, starting_word):
    running = True
    while running:
        wordl.run()
        #This creates informational arrays about color and position based on the type of website
        pos_info = [position_arr[0], position_arr[1], position_arr[2], position_arr[3]]
        col_info = [position_arr[4], position_arr[5], position_arr[6]]

        #Switching tabs
        # pyautogui.keyDown("alt")
        # pyautogui.press("tab")
        # pyautogui.keyUp("alt")

        #Starting with our initial word, trace, and calling our type_word method to type it on the website
        next_word = starting_word
        # by doing this, letters are entered into the word 
        type_word(next_word)



        #Since there are only 6 lines, we run this for loop MAX 6 times
        for x in range(6):

            #Resetting the arr_of_info and check_completion because our word changes each line
            arr_of_info = []
            check_completion = []

            #This is the list of colors and their rgb values determined from testing a separate program
            list_of_colors = [list(col_info[0]), list(col_info[1]), list(col_info[2])]

            #Getting the arr_of_info for the word we have just typed
            #time.sleep(3)
            arr_of_info = (wordl.wl.words[x], wordl.wl.getColors()[x], x)

            #This is where check_completion is amazingly efficient: If all() elements of check_completion are True, it returns True, otherwise it returns False
            #If the all() method returns True, it means every tile is green, so we break the for loop
            if all(check_completion):
                break

            #If all tiles are not green, then we go to the next word, determined by our "find_next" method, and type it
            next_word = find_next(arr_of_info, wordList)
            type_word(next_word)



wordList = wordl.word_dict



#These arrays contain positional values and rgb values for the different types of websites
archive_vals = [100, 100, wordl.wl.getWordDist(
), wordl.wl.getWordDist(), (58, 58, 60), (181, 159, 59), (83, 141, 78)]
real_website_vals = [1044, 444, 102, 102, (58, 58, 60), (181, 159, 59), (83, 141, 78)]

#Running the master method
wordle_solver(wordList,archive_vals, 'arose')
