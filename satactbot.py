import os
import praw
import sqlite3
import time
import heroku3
from apscheduler.schedulers.blocking import BlockingScheduler
from .herokuCodes import Codes 

SUMMONS = ['!SATACT', '!ACTSAT']
REPLY_TEMP = "beep boop\n\nThe equivalent " #ACT/SAT
REPLY_TEMP2 = " score to your " #ACT/SAT
REPLY_TEMP3 = " score is " #score
REPLY_TEMP4 = ".\n\n***\n\n^Data ^was ^provided ^by ^Collegeboard's ^Concordance ^tables ^last ^updated ^May ^9, ^2016 ^| ^Created ^by ^/u/Pianobin"
REPLY_TEMP5 = ". The equivalent "

ACTscores = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

SATscores = [560, 630, 720, 760, 810, 860, 900, 940, 980, 1020, 1060, 1100, 1130, 1160, 1200, 1240, 1280, 1310, 1350, 1390, 1420, 1450, 1490, 1520, 1560, 1600]

oldSATscores = [1610, 1620, 1640, 1650, 1670, 1680, 1700, 1710, 1730, 1750, 1760, 1780, 1790, 1810, 1820, 1840, 1850, 1870, 1880, 1900, 1920, 1930, 1950, 1970, 1990, 2000, 2020, 2040, 2060, 2080, 2090, 2110, 2130, 2150, 2170, 2190, 2210, 2230, 2260, 2280, 2300, 2330, 2350, 2370, 2390] #newSAT 1160 + 10x

def main():
	heroku_conn = heroku3.from_key(Codes.herkey)
	app = heroku_conn.apps()[Codes.herApp]
	print("Connected to Heroku (1/3)")
	config = app.config()
	getIDS(config)
	print("Config vars retrieved (2/3)")
	reddit = login_red()
	while True:
		run_app(reddit)
		time.sleep(60)
	#sched = BlockingScheduler(timezone="America/New_York")
	#print("timezone set (4/5)")
	#sched.add_job(lambda: run_app(reddit), 'cron', hour='6-23', minute='0-59')
	#print("Job scheduled (5/5)")
	#print("Ready to go!")
	#sched.start()	

def login_red():
	while True:
		try:
			reddit = praw.Reddit(user_agent='SatActBot (by /u/Pianobin)', username = login_us, password = login_pass, client_id= login_id, client_secret = login_sec)
			print("Logged into Reddit (3/3)")
			return reddit
		except:
			print("Couldn't login")
			time.sleep(120)

def run_app(reddit):	
	print("running app")
	try:
		subreddit = reddit.subreddit('SatActbot+ApplyingToCollege+Sat+ACT')
	except:
		print("Couldn't connect with subreddits")
		reddit = login_red
		subreddit = reddit.subreddit('SatActbot+ApplyingToCollege+Sat+ACT')
	openDB()
	for comment in subreddit.comments(limit=50):
		process_sub(comment)
	closeDB()
	print("Job complete, sleeping")
	localtime = time.asctime( time.localtime(time.time()) )
	print ("Local current time :", localtime)

def getIDS(config):
	global login_us
	global login_pass
	global login_id
	global login_sec
	dictIDS = config.to_dict()
	login_us = dictIDS['REDDIT_USERNAME']
	login_pass = dictIDS['REDDIT_PASSWORD']
	login_id = dictIDS['REDDIT_ID']
	login_sec = dictIDS['REDDIT_SEC']

def openDB():
	global db
	global cursor
	db = sqlite3.connect("Comment.db")
	cursor = db.cursor()

def closeDB():
	db.close()

def process_sub(comment):
	foundLink = False
	cursor.execute("""SELECT link FROM comments WHERE link=?""", (comment.permalink(),))
	for row in cursor:
		if comment.permalink() == row[0]:
			foundLink = True
			break	
	if foundLink:
		pass
	else:
		cursor.execute("""INSERT INTO comments
				(link)VALUES(?)""", (comment.permalink(),))
		db.commit()
		for summon in SUMMONS:
			if summon in str(comment.body).upper():
				commStr = str(comment.body)
				commStr = commStr + " AnotherWord "
				print(commStr)
				for num in commStr.split():
					if num.isdigit():
						theNum = int(num)
						print(theNum)
						if theNum >= 10 and theNum < 36: #ACT score provided
							theIndex = ACTscores.index(theNum)
							lowNum = SATscores[theIndex]
							highNum = SATscores[theIndex + 1] - 10		
							theType = "ACT"
							notTheType = "SAT"
							response = "between " + str(lowNum) + " and " + str(highNum) 
							print(response)
							reply_text = REPLY_TEMP + notTheType + REPLY_TEMP2 + theType + REPLY_TEMP3 + response + REPLY_TEMP4
						elif theNum == 36: #PERFECT ACT
							theType = "ACT"
							notTheType = "SAT"
							response = "1600"
							reply_text = REPLY_TEMP + notTheType + REPLY_TEMP2 + theType + REPLY_TEMP3 + response + REPLY_TEMP4
						elif theNum == 1600: #PERFECT SAT
							theType = "SAT"
							notTheType = "ACT"
							response = "36"
							reply_text = REPLY_TEMP + notTheType + REPLY_TEMP2 + theType + REPLY_TEMP3 + response + REPLY_TEMP4
						elif theNum >= 560 and theNum < 1600: #SAT provided
							nearScore = min(SATscores, key=lambda x:abs(x - theNum))
							print(nearScore)
							theIndex = SATscores.index(nearScore)
							if nearScore > theNum:
								theIndex = theIndex - 1
							ACT = ACTscores[theIndex]	
							theType = "new SAT"
							notTheType = "ACT"
							response = str(ACT)
							print(response)
							reply_text = REPLY_TEMP + notTheType + REPLY_TEMP2 + theType + REPLY_TEMP3 + response + REPLY_TEMP4
						elif theNum == 2400: #Perfect old SAT
							theType = "old SAT"
							notTheType = "ACT"
							notTheType2 = "new SAT"
							response = "36"
							response2 = "1600"
							reply_text = REPLY_TEMP + notTheType + REPLY_TEMP2 + theType + REPLY_TEMP3 + response + REPLY_TEMP5 + notTheType2 + REPLY_TEMP2 + theType + REPLY_TEMP3 + response2 + REPLY_TEMP4
						elif theNum >= 1610 and theNum <= 2390: #Old SAT
							theType = "old SAT"
							notTheType = "ACT"
							notTheType2 = "new SAT"

							nearScore = min(oldSATscores, key=lambda x:abs(x - theNum))
							theIndex = oldSATscores.index(nearScore)
							if nearScore > theNum:
								theIndex = theIndex - 1
							response2 = 1160 + 10 * theIndex #New SAT score

							nearScore2 = min(SATscores, key=lambda x:abs(x - response2))
							theIndex2 = SATscores.index(nearScore2)
							if nearScore2 > response2:
								theIndex2 = theIndex2 - 1
							response = ACTscores[theIndex2] #ACT score

							reply_text = REPLY_TEMP + notTheType + REPLY_TEMP2 + theType + REPLY_TEMP3 + str(response) + REPLY_TEMP5 + notTheType2 + REPLY_TEMP2 + theType + REPLY_TEMP3 + str(response2) + REPLY_TEMP4

						else: 
							print("Invalid number provided")
							theType = "invalid"
							notTheType = "invalid"
							response = "invalid"
							print(response)
							reply_text = "beep boop \n\n Sorry, the number you've given is outside of the range of checked scores. Be aware, the ACT scores below 11 and the SAT scores below 560 are not provided on Collegeboard's Concordance tables. \n\n Message /u/Pianobin with any concerns."
						print(reply_text)
						comment.reply(reply_text)
						break


if __name__ == '__main__':
	main()
