import logging


def logger(func):
    def wrapper(self, *argv, **kwargv):
        logging.info('%s %s %s', func.__name__, ' '.join(map(str, argv)), kwargv)
        try:
            ret = func(self, *argv, **kwargv)
        except Exception as e:
            logging.error(e.__class__.__name__)
            raise e
        logging.info('%s return %s', func.__name__, ret)
        return ret
    return wrapper
