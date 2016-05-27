import datetime
import settings
import traceback


def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        log('UnicodeEncodeError, can\'t repeat the unencodable character!')
    except Exception as e:
        with open(settings.ERROR_FILENAME, 'a') as out_file:
            out_file.write(repr(e) + '\n')
            out_file.write(traceback.format_exc() + '\n')
        log('Unknown error with type: {}, logged to error.txt'.format(type(e)))
    if settings.LOG_TO_FILE:
        with open(settings.LOG_FILENAME, 'a') as out_file:
            out_file.write('{}{}\n'.format(datetime.datetime.now(), msg))


def log_error(msg, e):
    msg = '{}: {}\n{}\n'.format(msg, repr(e), traceback.format_exc())
    log(msg)

