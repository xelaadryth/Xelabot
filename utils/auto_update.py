import os
import settings
import subprocess
import sys
import urllib.request


from utils.logger import log


# Rename the executable and then run it
RENAME_BATCH_SCRIPT = ':: Waiting for xelabot.exe to close\ntimeout 5\nmove /y {0} {1}\n{1}\n'.format(
    settings.NEW_EXECUTABLE_FILENAME, settings.EXECUTABLE_FILENAME)


def update_executable():
    """
    Get the replacement executable and swap it with the running one using a batch script.
    """
    log('Updating...')
    urllib.request.urlretrieve(settings.BASE_URL + settings.EXECUTABLE_FILENAME, settings.NEW_EXECUTABLE_FILENAME)

    with open(settings.RENAME_SCRIPT_FILENAME, 'w') as write_file:
        write_file.write(RENAME_BATCH_SCRIPT)

    subprocess.Popen(settings.RENAME_SCRIPT_FILENAME, creationflags=subprocess.CREATE_NEW_CONSOLE)
    sys.exit(0)


def latest_version():
    """
    Check the latest version of xelabot.
    :return: str - The latest version number posted online
    """
    log('Checking version...')
    with urllib.request.urlopen(settings.BASE_URL + settings.VERSION_FILENAME) as version_file:
        newest_version = version_file.readline().decode(encoding='UTF-8').strip()

    return newest_version == settings.VERSION


def try_update():
    """
    Checks the latest version number and prompts to update.
    """
    # Check if we're an executable or not
    if not os.path.isfile(settings.EXECUTABLE_FILENAME):
        # Probably dev environment, don't run version checking
        return

    if not latest_version():
        if not settings.AUTO_UPDATE_EXECUTABLE:
            response = input('Newer version of Xelabot detected. Would you like to update? (y/n): ')

            if not response.lower() in ['y', 'yes']:
                log('Well, we can always update later. :(')
                return

        update_executable()
