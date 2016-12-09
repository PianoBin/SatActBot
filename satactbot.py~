import praw
import bot

def main():
	reddit = praw.Reddit(user_agent='SatActBot (by /u/Pianobin)', username = bot.user, password = bot.pw, client_id= bot.idS, client_secret = bot.idSec)
	subreddit = reddit.subreddit('SatActbot')
	for submission in subreddit.new(limit=10):
		print(submission.title)
		print(submission.url)
