import logging


def logger(func):
    def wrapper(self, *argv, **kwargv):
        logging.info('%s %s %s %s', __name__, func.__name__, argv, kwargv)
        try:
            ret = func(self, *argv, **kwargv)
        except Exception as e:
            logging.error(e.__doc__)
            raise e
        logging.info('%s %s return %s', __name__, func.__name__, ret)
        return ret
    return wrapper
