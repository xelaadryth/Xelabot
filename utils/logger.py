import settings
import traceback


def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        log('UnicodeEncodeError, can\'t repeat the unencodable character!')
    if settings.LOG_TO_FILE:
        with open(settings.LOG_FILENAME, 'a') as out_file:
            out_file.write(msg + '\n')


def log_error(msg, e):
    msg = '{}: {}\n{}\n'.format(msg, repr(e), traceback.format_exc())
    log(msg)

