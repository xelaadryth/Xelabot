import settings
import traceback


def log(msg):
    print(msg)
    with open(settings.LOG_FILENAME, 'a') as out_file:
        out_file.write(msg)


def log_error(msg, e):
    msg = '{}: {}\n{}'.format(msg, repr(e), traceback.format_exc())
    log(msg)

