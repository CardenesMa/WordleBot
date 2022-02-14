# Code Author: Marco Cardenes
# Special thanks to Kush Bandi and Niel Wagner-Oke for the help with the bot
# Thanks to Jackson Zemek for help with the visual design

# This program shows a bot that plays wordle and shows the stats etc.

# used to draw the bots actions
import pygame
# used to choose a random word for the bot to solve for
import random
# used to get the information from the .ini file
import configparser
# used to write the ml data
import csv


# take inputs form the config (.ini) file 
config = configparser.ConfigParser()
config.read("wordl.ini")

# .ini's always return strings, so i need to turn the string into a tuple
def parse_tuple(input):
	return tuple(int(k.replace("(","").replace(")","")) for k in input[1:-1].split(','))


consts = config['CONSTS']
locs = config['LOCATIONS']
#!
framerate = float(consts["framerate"])

test_word = consts["starting_word"]
word_list = [test_word]

# create the list of 5 letter words
with open(locs["word_list"], "r") as f:
	for i in f.readlines():
		for word in i.split(","):
			word_list.append(word.upper().replace("\"", ""))

### Constants ###
height, width = int(consts["height"]), int(consts["width"])
grey, orange, green, white, red = parse_tuple(consts["grey"]), parse_tuple(consts["orange"]), parse_tuple(consts["green"]), parse_tuple(consts["white"]),parse_tuple(consts["red"])
padding = int(consts["padding"])
# this is to offset the location of the letters because it looks strange
letter_correct = int(consts["letter_correction"])
# initializing the font 
font_family = consts["font_family"]

# box sizes (prioritizing height for square)
sizey = int((height-7*padding)/8)
sizex = sizey

# this is saying whether or not to create training data for the wordl_ml.py file
make_data = bool(consts["make_data"])

# choosing where to draw the pygame board
offsetx, offsety = int(width/2-2.5*sizex-2*padding), height/5

# load up the checkmark and x
checkmark = pygame.image.load(locs['checkmark_location'])
x_img = pygame.image.load(locs['cross_image_location'])

checkmark = pygame.transform.scale(checkmark,(sizex*5, sizey*6))
x_img = pygame.transform.scale(x_img, (sizex*5, sizey*6))

# start pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption("Wordle")
font = pygame.font.SysFont(font_family, int(sizex*0.75))
clock = pygame.time.Clock()

word_input_sound = pygame.mixer.Sound(locs['word_sound_file'])
wrong_sound = pygame.mixer.Sound(locs["incorrect_sound_file"])
right_sound = pygame.mixer.Sound(locs["correct_sound_file"])


class Word:
	def __init__(self, secret_word):
		self.secret_word = secret_word
		self.chars = ""
		self.colors = []
		
	def addLetter(self, letter):
		# only add a letter if there are too few characters
		if len(self.chars) < len(self.secret_word):
			# add a letter to the word
			self.chars += letter
			return self.chars 
	
	def checkFinal(self):
		# if the inputted word is the same as the secret word
		self.check()
		if self.chars == self.secret_word:
			self.colors = [green for i in range(5)]
			return True
		else:
			return False 

	def check(self):
		if self.chars in word_list:
			# make the color list be complete
			self.makeColors()
			return True
		return False

	def delLetter(self):
		self.chars = self.chars[:-1]
		return self.chars 
	
	def makeColors(self):
		for index, letter in enumerate(self.chars):
			# if the letter is in the correct place
			if self.chars[index] == self.secret_word[index]:
				self.colors.append(green)
			# if it's actually in the word at all
			elif letter in self.secret_word:
				self.colors.append(orange)
			# if not, then it's not a used letter
			else:
				self.colors.append(grey)
		return self.colors 

class WordBoard:
	def __init__(self, secret:str):
		self.isComplete = False
		# the secret word
		self.secret = secret
		# list of all the Words 
		self.words = [Word(self.secret) for i in range(6)]
	
	# puts a word into the word lsit based on the string input
	
	def checkComplete(self, index:int):
		# if the last word is all green
		if self.words[index].checkFinal():
			self.isComplete = True
			return True 
		return False 
	
	def checkWord(self, word_index:int):
		# if it's a real word...
		if self.words[word_index].chars in word_list:
			# make the colors
			self.words[word_index].makeColors()
			return True
		return False 

class Displayer:
	def __init__(self, wordBoard: WordBoard):
		# keeps track of what word we're on
		self.word_index = 0

		self.wordBoard = wordBoard
	
	def display(self):
		# i is a Word type of all the words within our wordBoard
		for ind, i in enumerate(self.wordBoard.words):
			# get the colors
			# if no colors are made,
			if len(i.colors) < 5:
				# makke it all grey
				colors = [grey for i in range(5)]
			# otherwise, colors are made, so use those
			else:
				colors = i.colors

			# for some reason it doesn't display once it's been checked, so I'm going to try to artificially check it and draw the green boxes
			for j in range(5):
				
				# make the boxes
				x_loc,y_loc = j*(sizex+padding) + offsetx, ind*(sizey+padding) + offsety
				pygame.draw.rect(screen,colors[j],pygame.Rect(x_loc, y_loc, sizex, sizey))
				# make the letters
				# because the whole word might not be written out yet, try it
				try:
					letter = font.render(i.chars[j], True, white)
				except:

					letter = font.render(" ", True, white)				# write the letter to the screen
				screen.blit(letter,(x_loc+sizex/4+letter_correct,y_loc+sizey/4))
		
			
	def checkComplete(self):
		k = self.wordBoard.checkComplete(self.word_index)
		if k:
			self.reset()
			return True
		
		return False

	def check(self):
		if self.word_index == 5:
			self.reset()
		# if the word at the current index works, then continue
		self.checkComplete()
		if self.wordBoard.checkWord(self.word_index):
			self.word_index += 1
			return True 

		return False

	def cw(self):
		# gets the current word and returns it
		return self.wordBoard.words[self.word_index]


	def addLetter(self, letter):
		self.cw().addLetter(letter)

	def delLetter(self):
		self.cw().delLetter()

	def reset(self):
		self.word_index = 0
		
		random_word = word_list[random.randint(0, len(word_list)-1)]
		self.wordBoard = WordBoard(random_word)
		
	
	def getWords(self):
		return self.wordBoard.words

	def makeGreenFinal(self, y_location, word):
		for i in range(5):
			x_loc, y_loc = i*(sizex+padding) + offsetx, y_location*(sizey+padding) + offsety
			pygame.draw.rect(screen, green, pygame.Rect(x_loc, y_loc, sizex, sizey))
			letter = font.render(word[i], True, white)				# write the letter to the screen
			screen.blit(letter, (x_loc+sizex/4+letter_correct, y_loc+sizey/4))
	def makeRedBoxes(self):
		for j in range(5):
			for ind in range(6):
			# make the boxes
				x_loc, y_loc = j*(sizex+padding) + offsetx, ind*(sizey+padding) + offsety
				pygame.draw.rect(screen, red, pygame.Rect(x_loc, y_loc, sizex, sizey))
		
class Info:
	def __init__(self, Displayer:Displayer):
		self.disp = Displayer 
	
	def getWords(self):
		return self.disp.getWords()
	
	def getColors(self):
		return [self.getWords()[i].colors for i in range(6)]
	
	def getComplete(self):
		return self.disp.checkComplete()


def makeInfo(info:Info):
	final = []
	# get all the words available
	for word in info.getWords():
		# assign their values as the character strings within them
		c_word = word.chars
		colors = word.colors
		for index, letter in enumerate(c_word):
			final.append([letter,colors[index],index])
	return final


#This function eliminates words from wordList depening on colors of tiles
def nextBestWord(info_arr:Info):

	wordList = list(word_list)
	info_arr = makeInfo(info_arr)

	#Running this whole loop section several times due to python not parsing properly
	for i in range(6):

		#Looking at our informational array
		for x in info_arr:

			#If the color in our info_array is grey, we don't want any words that have that letter
			if x[1] == grey:

				#The following for loop removes all words in wordList with that letter
				for word in wordList:

					#However, we need to check if the letter exists and is green to ensure we don't accidentally remove words
					letter_exists = False

					#Going through the info_arr again to do the previous statement
					for y in info_arr:

						#If we encounter our current letter AND it has the green attribute, set the boolean to true
						if (x[0] == y[0]) and (y[1] == green):
							letter_exists = True

					#If the boolean is false and the grey letter is in a word, remove it
					if x[0] in word and not letter_exists:
						wordList.remove(word)

			#If the color in our info_array is green, we only want words that have that letter in that position
			elif x[1] == green:

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

def successScreen():
	screen.blit(checkmark, (offsetx+letter_correct*5,offsety+letter_correct*2))
	pygame.mixer.Sound.play(right_sound)
	clock.tick(framerate*2)


def failScreen():
	screen.blit(x_img, (offsetx+letter_correct*5,offsety+letter_correct*8))
	pygame.mixer.Sound.play(wrong_sound)

def drawTitle():
	# draw the title
	titlefont = pygame.font.SysFont(font_family, int(sizex))
	text = titlefont.render("WORDLE", True, white)
	screen.blit(text, (offsetx + sizex + padding, offsety/3))
	# little vector design
	pygame.draw.line(screen, white, (offsetx + sizex-padding, 2*offsety/3+padding*2),(offsetx + sizex*4+ padding*4, 2*offsety/3+padding*2),5)
 
def drawStats(total,divisor, failed = [], streak = 0, streaks_list = [], framerate = 0, secret = "", int_frm = 0):

	distancey = 20
	distancex = padding*2
	# just in case we froget what anumber stat we're on
	index = 1
	# make the fonts
	accuracyfont = pygame.font.SysFont(font_family, int(sizex/4))
	statsfont = pygame.font.SysFont(font_family, int(sizex/3))

	# draw the Stats: title
	stattitle = statsfont.render("Stats:", True, white)
	screen.blit(stattitle, (distancex, offsety-padding))

	# make a little vector art
	pygame.draw.line(screen,white,(distancex,offsety+distancey/2), (distancex + 2*sizex/3, offsety + distancey/2))

	word = accuracyfont.render(f"Test Word: {test_word}", True, white)
	screen.blit(word, (distancex, offsety+distancey*index))
	index += 1

	if divisor > 0:
		score = accuracyfont.render(f"Success Rate: {round(total/divisor*100,2)}%",True,white)
	else:
		score = accuracyfont.render("Success Rate: No Games Played",True, white)
	
	screen.blit(score, (distancex, offsety+distancey*index))
	index += 1

	# show games played
	played = accuracyfont.render(f"Games Played: {total}", True, white)
	screen.blit(played, (distancex, offsety+distancey*index))
	index += 1

	won = accuracyfont.render(f"Games Won: {divisor}", True, white)
	screen.blit(won, (distancex, offsety+distancey*index))
	index += 1
	# show what word is the one we're starting with to test out the program (best is )

	streakword = accuracyfont.render(f"Current Streak: {streak}", True, white)
	screen.blit(streakword, (distancex, offsety + distancey*index))
	index += 1

	longest = accuracyfont.render(f"Longest Streak: {max(streaks_list)}", True, white)
	screen.blit(longest, (distancex, offsety+distancey*index))
	index += 1 

	secretword = accuracyfont.render(f"Secret Word: {secret}", True, white)
	screen.blit(secretword, (distancex, offsety + distancey*index))
	index += 1

	if framerate < 1 and framerate > 0:
		framerate = 1/framerate 
		frametitle = accuracyfont.render(f"Framerate: {framerate} seconds per frame", True, white)
	else:
		frametitle = accuracyfont.render(f"Framerate: {framerate} fps", True, white)
	screen.blit(frametitle, (distancex, offsety+distancey*index))
	index += 1 

	intfrm = accuracyfont.render(f"Intended Framerate: {int_frm}", True, white)
	screen.blit(intfrm, (distancex, offsety+distancey*index))
	index += 1 

	prct = accuracyfont.render(f"Amount of Dataset Played: {round(total/len(word_list)*100,2)}%", True, white)
	screen.blit(prct, (distancex, offsety+distancey*index))
	index += 1

	prctloss = accuracyfont.render(f"Percentage of Dataset Gotten Wrong: {round(len(failed)/len(word_list)*100,2)}%", True, white)
	screen.blit(prctloss, (distancex, offsety+distancey*index))
	index += 1

	failedtitle = accuracyfont.render("Failed Words:", True, white)
	screen.blit(failedtitle, (distancex, offsety+distancey*index))
	index += 1

	for failedword in failed:
		failedwordstring = accuracyfont.render("   "+failedword, True, white)
		screen.blit(failedwordstring, (distancex, offsety+distancey*index))
		index += 1
	

def drawCredits():
	string = "Created by Marco Cardenes with help from Kush Bandi, Niel Wagner-Oke and Jackson Zemek. Word dataset from the official Wordle."
	creditfont = pygame.font.SysFont(font_family, int(sizex/4))
	credits = creditfont.render(string, True, white)
	screen.blit(credits, (padding, height-sizex/4-padding))


class Graph:
	def __init__(self):
		self.pair_list = []
		self.x_gap = 2
		self.x_max = sizex*4/self.x_gap
		self.scaler = 1/5
		self.bl_loc = (11*width/15, offsety+1/self.scaler*100)
	
	def addPair(self, success, total):
		if total < 1:
			pass
		elif len(self.pair_list) == self.x_max:
			self.pair_list = self.pair_list[1:]
			self.pair_list.append((total, round(success/total*100,2)))
		else:
			self.pair_list.append((total, round(success/total*100,2)))
	
	def display(self):
		x_gap = self.x_gap
		scaler = self.scaler


		# draw graph vertical line and 100% text
		pygame.draw.line(screen, white, self.bl_loc, (self.bl_loc[0],self.bl_loc[1]-1/scaler*100),2)
		ptxt = pygame.font.SysFont(font_family, int(sizex/4))
		t = ptxt.render("100%-", True, white)
		screen.blit(t, (self.bl_loc[0]-sizex/4*2, self.bl_loc[1]-1/scaler*100-sizex/16))
		# horizontal and 0% text
		pygame.draw.line(screen, white, self.bl_loc, (self.bl_loc[0]+self.x_gap*self.x_max, self.bl_loc[1]),2)
		noptxt = ptxt.render("0%-", True, white)
		screen.blit(noptxt, (self.bl_loc[0]-sizex/3, self.bl_loc[1]-sizex/16))

		if len(self.pair_list) > 2:
			for i in range(len(self.pair_list)-1):
				# define the scaled values
				currentscaledy = self.pair_list[i][1]/scaler
				nextscaledy = self.pair_list[i+1][1]/scaler
				# current coordinates
				currentx = i*x_gap + self.bl_loc[0]
				currenty = self.bl_loc[1]-currentscaledy
				# next coordinates
				nextx = (i+1)*x_gap + self.bl_loc[0]
				nexty = self.bl_loc[1]-nextscaledy

				if self.pair_list[i][1] > self.pair_list[i+1][1]:
					pygame.draw.line(screen, red, (currentx,currenty),(nextx,nexty),3)
				else:
					pygame.draw.line(screen, green, (currentx,currenty),(nextx,nexty),3)
		label = pygame.font.SysFont(font_family, int(sizex/4))
		labeld = label.render("Accuracy v Rounds", True, white)
		screen.blit(labeld, (self.bl_loc[0]+(x_gap*scaler)/2-sizex/4, self.bl_loc[1]+sizex/4))


def makeData(allwords:list):
	#! isCorrect outdated, only make data if correct. Colors?
	header = ["Word 1", "Word 2", "Word 3", "Word 4", "Word 5", "Word 6", "Correct Word"]
	with open("wordle_data.csv","w") as f:
		csvwriter = csv.writer(f)
		# write that header
		csvwriter.writerow(header)

		csvwriter.writerows(allwords)



#  start making pygame
def run(Displayer:Displayer):
	# guesses holds the number of words it's guessed within a game
	guesses = 0
	# default
	best_word = test_word
	# constants for running the game
	info = Info(Displayer)
	graph = Graph()
	running = True 
	success = False
	show_stats = True
	# used to calculate the effectivenenss of the bot
	success_count = 0
	games_played = 0
	failed_words = []
	streak = 0 
	streak_list = [0]
	# this is used because it doens't actually make teh green boxes for the final correct word, so it's stored here
	green_word = ""
	frm = framerate
	# this will hold the data for the machine learning in another file
	ml_data = []
	# this holds the gameplay data one at a time (so as not to destroy memory in case it needs to be replaced)
	temp_data = []
	while running:
	
		# fill background
		screen.fill((19,18,21))

		clock.tick(frm)

		# uncomment this if you want to see the center line of the canvas
		# pygame.draw.line(screen,red,(width/2,0),(width/2,height))

		# draw the title
		drawTitle()
		drawCredits()


		
		# getting the events
		for event in pygame.event.get():
			# quit when necessary
			if event.type == pygame.QUIT:
				running=False 
			
			if event.type == pygame.KEYDOWN:
				key = pygame.key.name(event.key)
				if key == "9":
					print(Displayer.wordBoard.secret)
				elif key == "q":
					running = False
				elif key == "s":
					show_stats = not show_stats
				elif key == "up":
					frm = 100
				elif key == "down":
					frm = 1
		

		temp_data.append(best_word)
		# play the game
		secret_word = Displayer.wordBoard.secret
		Displayer.check()
		# write the word into the screen
		best_word = nextBestWord(info)
		
		# save that word into the temporary data
		# write the best word into the game
		for i in best_word:
			Displayer.addLetter(i)

		#display it
		Displayer.display()

		guesses += 1
		if success:
			# for the machine learning
			if make_data:
				# this is to put empty space for unused words
				if guesses < 6:
					for i in range(6-guesses):
						temp_data.append("     ")
				temp_data.append(green_word)
				ml_data.append(temp_data)
				temp_data = []
			
			successScreen()
			Displayer.makeGreenFinal(guesses-1,green_word)
			guesses=0
			success=False
			games_played += 1
			success_count += 1
			streak += 1

		elif not success and guesses==6:
		
			Displayer.makeRedBoxes()
			failScreen()
			if secret_word not in failed_words:
				failed_words.append(secret_word)
			games_played += 1
			streak_list.append(streak)
			streak = 0
			temp_data = []
			if make_data:
				temp_data.append(green_word)
				ml_data.append(temp_data)
				temp_data = []
		
		else:
			pygame.mixer.Sound.play(word_input_sound)

		# put this afterward so that it loops back around and draws later
		l = Displayer.checkComplete()
		if l:
			success = True
			green_word = secret_word
		
		# draw the stats if that's an option
		if show_stats:
			# framerate intention reasoning 
			if frm > 1:
				drawStats(success_count,games_played, failed=failed_words, streak = streak, streaks_list=streak_list, framerate = round(clock.get_fps()), secret = secret_word, int_frm = frm)
			else:
				drawStats(success_count,games_played, failed=failed_words, streak = streak, streaks_list=streak_list, framerate = frm, secret = secret_word, int_frm = frm)
	

			graph.addPair(success_count,games_played)

			graph.display()

			

		pygame.display.flip()

	# this is outside of the loop
	if make_data:
		makeData(ml_data)
	pygame.quit()

def requirements():
	print("""
	Create WordBoard(secret_word)\n
	Create Displayer(WordBoard)\n
	To get info, use Info(Displayer)\n
	run(displayer) to show the information on the screen
	""")

wb = WordBoard(test_word)
d = Displayer(wb)
run(d)
