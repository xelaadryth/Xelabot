import os
import settings
import subprocess
import sys
import urllib.request


from utils.logger import log


TEMP = 'temp_'
RENAME_SCRIPT_FILENAME = TEMP + 'rename.bat'
NEW_EXECUTABLE_FILENAME = TEMP + settings.EXECUTABLE_FILENAME
# Rename the executable and then run it
RENAME_BATCH_SCRIPT = ':: Waiting for xelabot.exe to close\ntimeout 5\nmove /y {0} {1}\n{1}\n'.format(
    NEW_EXECUTABLE_FILENAME, settings.EXECUTABLE_FILENAME)


def update():
    log('Updating...')
    urllib.request.urlretrieve(settings.BASE_URL + settings.EXECUTABLE_FILENAME, TEMP + settings.EXECUTABLE_FILENAME)

    with open(RENAME_SCRIPT_FILENAME, 'w') as write_file:
        write_file.write(RENAME_BATCH_SCRIPT)

    subprocess.Popen(RENAME_SCRIPT_FILENAME, creationflags=subprocess.CREATE_NEW_CONSOLE)
    sys.exit(0)


def clear_temp_files():
    if os.path.isfile(RENAME_SCRIPT_FILENAME):
        os.remove(RENAME_SCRIPT_FILENAME)
    if os.path.isfile(NEW_EXECUTABLE_FILENAME):
        os.remove(NEW_EXECUTABLE_FILENAME)


def latest_version():
    log('Checking version...')
    with urllib.request.urlopen(settings.BASE_URL + settings.VERSION_FILENAME) as version_file:
        newest_version = version_file.readline().decode(encoding='UTF-8').strip()

    return newest_version == settings.VERSION


def try_update():
    # Check if we're an executable or not
    if not os.path.isfile(settings.EXECUTABLE_FILENAME):
        # Probably dev environment, don't run version checking
        return

    if not latest_version():
        response = input('Newer version of Xelabot detected. Would you like to update? (y/n): ')

        if response.lower() in ['y', 'yes']:
            update()
        else:
            log('Well, we can always update later. :(')
