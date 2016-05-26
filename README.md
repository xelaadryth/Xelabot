# Xelabot
A game in the form of a Twitch chat bot.

## Developer Setup Instructions (Windows)
- Install Python 3.4+
- Add Python34 and Python34/Scripts to your system PATH
- Run setup.bat to set up your virtual environment and install required packages
- Build with build.bat to use that virtual environment to run PyInstaller to build to standalone .exe
- Run the standalone executable "../dist/xelabot.exe"
- For auto-update, change settings.BASE_URL and keep the following files available for download:
 - xelabot.exe (from /dist/xelabot/xelabot.exe)
 - version.txt (A file whose only contents is a string of settings.VERSION)

## To Do List:
- All quest commands can take whispers (as optional setting?)
- https://tmi.twitch.tv/group/user/USERNAME_HERE/chatters to check current viewers for loyalty bumps
- Raid quest
- Multi-bot communication whisper hash handshake (bot names combined hash to value) and bot storage
- Update raid quest with war
