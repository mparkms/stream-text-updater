from Tkinter import *
import challonge
from urlparse import urlparse
from urllib2 import HTTPError
from tkMessageBox import *

challonge.set_credentials("CHALLONGE ID", "CHALLONGE API KEY")

class PlayerNotFoundError(Exception):

	# Raised when the given player ID is not found in the list of players.
	# Probably should never be raised barring some fatal unknown error or a change in the Challonge API.
	def __init__(self):
		return

class App:

	def __init__(self, master):
		# Labels
		infoLabel = Label(master, text="Infotext")
		p1Label = Label(master, text="Player 1")
		p2Label = Label(master, text="Player 2")
		cam1Label = Label(master, text="Cam 1")
		cam2Label = Label(master, text="Cam 2")
		scoreLabel = Label(master, text="Score")
		scoreLabel2 = Label(master, text="Score")

		infoLabel.grid(sticky=E)
		p1Label.grid(sticky=E)
		p2Label.grid(sticky=E)
		cam1Label.grid(sticky=E)
		cam2Label.grid(sticky=E)
		scoreLabel.grid(row=1, column=2)
		scoreLabel2.grid(row=2, column=2)

		# Entry boxes
		self.infoEntry = Entry(master, width=50)
		self.p1Entry = Entry(master, width=40)
		self.p1Score = Entry(master, width=2)
		self.p2Entry = Entry(master, width=40)
		self.p2Score = Entry(master, width=2)
		self.cam1Entry = Entry(master, width=50)
		self.cam2Entry = Entry(master, width=50)

		self.infoEntry.grid(row=0, column=1, columnspan=3)
		self.p1Entry.grid(row=1, column=1)
		self.p1Score.grid(row=1, column=3)
		self.p2Score.grid(row=2, column=3)
		self.p2Entry.grid(row=2, column=1)
		self.cam1Entry.grid(row=3, column=1, columnspan=3)
		self.cam2Entry.grid(row=4, column=1, columnspan=3)

		# Update button
		updateButton = Button(master, text="Update", command=self.printContents)

		updateButton.grid(columnspan=4, pady=2)

		# Manual ticker text
		tickerLabel = Label(master, text="Ticker")
		self.tickerEntry = Entry(master, width=50)
		tickerLabel.grid(sticky=E)
		self.tickerEntry.grid(row=6, column=1, columnspan=3)
		# Challonge label/entry box/button
		challongeLabel = Label(master, text="Challonge")
		self.challongeLink = Entry(master, width=50)
		challongeLabel.grid(sticky=E)
		self.challongeLink.grid(row=7, column=1, columnspan=3)

		challongeButton = Button(master, text="Update ticker", command=self.updateTicker)
		challongeButton.grid(columnspan=4, pady=2)

	def printContents(self):

		info = self.infoEntry.get()
		p1 = self.p1Entry.get()
		p2 = self.p2Entry.get()
		cam1 = self.cam1Entry.get()
		cam2 = self.cam2Entry.get()
		score1 = self.p1Score.get()
		score2 = self.p2Score.get()

		with open('files/info.txt', 'w') as f:
			f.write(info)
		with open('files/p1.txt', 'w') as f:
			f.write(p1)
		with open('files/p2.txt', 'w') as f:
			f.write(p2)
		with open('files/cam1.txt', 'w') as f:
			f.write(cam1)
		with open('files/cam2.txt', 'w') as f:
			f.write(cam2)
		with open('files/score1.txt', 'w') as f:
			f.write(score1)
		with open('files/score2.txt', 'w') as f:
			f.write(score2)

	def updateTicker(self):

		link = self.challongeLink.get()
		text = self.tickerEntry.get()

		if (link == ""):				#if entry box is blank
			self.printTicker(text + " ")
			return

		try:
			uri = self.parseLink(link)		#parse correct URI from URL
		except:
			showerror("Error", "Invalid URL")
			return
		
		try:
			matches = challonge.matches.index(uri) #get all matches
		except HTTPError as e:
			showerror("Error", "Error: " + str(e.code) + " (" + e.reason + ")")
			return

		players = challonge.participants.index(uri) #get all players
		results = self.processMatches(matches, players)	#returns correct results feed

		if (text == ""):
			self.printTicker(results)
		else:
			ticker = text + " - " + results
			self.printTicker(ticker)

	def parseLink(self, link):

		uri = ""
		parsed = urlparse(link)

		if (parsed.netloc == ""):					#if no http://
			pathSplit = parsed.path.split(".")
			if (len(pathSplit) == 3):				#www.(subdomain).challonge.com is not possible
				if (pathSplit[0] == "www"):			#if www.challonge.com/...
					uri = ""
				else:								#if (subdomain).challonge.com
					uri = pathSplit[0] + "-"
				nameSplit = pathSplit[2].split("/")	#get name of bracket
				uri = uri + nameSplit[1]
			else:									#if challonge.com/...
				nameSplit = pathSplit[1].split("/")
				uri = uri + nameSplit[1]
		else:										#if there is http://
			netlocSplit = parsed.netloc.split(".")
			if (len(netlocSplit) == 3):
				if (netlocSplit[0] == "www"):		#if www.challonge.com/...
					uri = ""
				else:								#if (subdomain).challonge.com
					uri = netlocSplit[0] + "-"
			uri = uri + parsed.path[1:]				#get name of bracket

		return uri 									#should be of form (subdomain)-(name)

	def processMatches(self, matches, players):

		#for match in matches:
		#	print(match["identifier"])
		filtered = filter(lambda x: x["scores-csv"] != None, matches) 	#filter out all matches w/o scores

		filteredW = filter(lambda x: x["round"] > 0, filtered)			#winners has round > 0
		filteredL = filter(lambda x: x["round"] < 0, filtered)			#losers has round < 0

		#print(filteredW)

		try:
			return self.printMatches(filteredW, filteredL, players)
		except PlayerNotFoundError:
			showerror("Error", "Error: player not found. If you see this message, contact me at @kaabistar.")

	def printMatches(self, winners, losers, players):
		
		toPrint = ""

		if (len(winners) > 3):
			winners = winners[-3:]
		if (len(losers) > 3):
			losers = losers[-3:]

		for match in winners:
			toPrint = toPrint + "WR" + str(match["round"]) + ": "
			player1ID = match["player1-id"]
			player2ID = match["player2-id"]
			player1 = self.getPlayer(player1ID, players)
			player2 = self.getPlayer(player2ID, players)
			toPrint = toPrint + player1 + " " + match["scores-csv"] + " " + player2 + " "

		for match in losers:
			toPrint = toPrint + "LR" + str(match["round"])[1:] + ": "
			player1ID = match["player1-id"]
			player2ID = match["player2-id"]
			player1 = self.getPlayer(player1ID, players)
			player2 = self.getPlayer(player2ID, players)
			toPrint = toPrint + player1 + " " + match["scores-csv"] + " " + player2 + " "

		return toPrint

	def getPlayer(self, pid, players):

		for player in players:
			if (player["id"] == pid):
				return player["name"]
		raise PlayerNotFoundError()	#probably should never happen
	
	def printTicker(self, ticker):

		with open ('files/ticker.txt', 'w') as f:
			f.write(ticker)

master = Tk()
master.wm_title("Stream Text Updater")

app = App(master)

master.mainloop()