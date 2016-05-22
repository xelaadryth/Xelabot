# Xelabot
A game in the form of a Twitch chat bot.

Download the project, modify the settings.py file, and then run xelabot.bat to activate!

Important! Make you have Python version 3 installed.

Usage Instructions:
	To call Xelabot into your channel, just type !requestjoin in http://www.twitch.tv/xelaadryth.

	Please mod Xelabot in your channel to improve performance, it really helps a lot. Thanks!

	Note that Xelabot posts links for some commands.


Commands usable only in http://www.twitch.tv/xelabot:
	!requestjoin
		Makes the bot join your channel (until told to leave)
	!requestleave
		Makes the bot leave your channel (until told to leave)


Basic Commands
	!xelabot
		Links this guide
	!quest
		Starts a quest or joins a forming party (if !queston command was given)
	!stats
		Gives the link to the global player stats page (updates every minute or so)
	!prestige
		Attempts to prestige, losing 30 levels of experience and a large sum of gold to increase prestige level, which amplifies gold accumulation


Mod Commands
	!comadd ![commandname] [reply]
		Adds ![commandname] as a command where Xelabot will reply with [reply]
	!comdel ![commandname]
		Removes !commandname as a command
	!comlist
		Lists all of Xelabot's commands for the current channel
	!queston
		Enables quest commands
	!questoff
		Disables quest commands
	!questcooldown [seconds]
		Sets the cooldown for quests to the given number of seconds
	!filteron
		Enables banning for a small list of phrases (bot spam links usually)
	!filteroff
		Disables banning filter


FREQUENTLY ASKED QUESTIONS
	I just gained exp and gold but it didn't update in the !stats link!
		The document with stats takes about a minute to update after being modified!
	Can my gold go negative?
		Nope, not anymore!
	What is prestige?
		To prestige you sacrifice 30 levels of experience and 30,000 gold to gain a prestige level. Each prestige level increases gold accumulation by 5%.
	Are my stats channel-specific?
		Stats are saved globally, so your stats in one channel carry over to another.
	Is the quest cooldown per person or per channel?
		The quest cooldown timer is per channel.
	I tried what you said but it still doesn't work!
		Feel free to message me, I'll be happy to help!


If you have any feedback or questions, feel free to message me, Xelaadryth!
http://www.twitch.tv/xelaadryth
https://www.twitter.com/xelaadryth

## To Do List:
- Fix and refactor existing tech
- https://tmi.twitch.tv/group/user/USERNAME_HERE/chatters to check current viewers for loyalty bumps
- Encrypt player stats?
