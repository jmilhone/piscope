from __future__ import print_function, division
import logging
from functools import wraps
import time

def create_logger(name='pi-scope-logger', filename='piscope-debug.log', useNull=False):
    """
    Returns a logging.Logger object

    Args:
        name (str): Name of the Logger object
        filename (str): Filename to write log output to if useNull is False
        useNull (bool): True if logging should be disabled and a NullHandler will be used

    Returns:
        a logging.Logger object
    """
    logger = logging.getLogger(name)

    if useNull:
        handler = logging.NullHandler
    else:
        handler = logging.FileHandler(filename=filename, mode='w')
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%m/%d/%Y %I:%M:%S %p')

        handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def log(logger):
    """
    A decorator that wraps the passed in function and logs

    Args:
        logger (logging.Logger): the logging object
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug('Calling function %s' % func.__name__)
            try:
                return func(*args, **kwargs)
            except:
                logger.exception('Error in %s' % func.__name__)
                raise
        return wrapper

    return decorator


def time_log(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                t0 = time.time()
                res = func(*args, **kwargs)
                t1 = time.time()
                logger.debug('Calling function %s, completed in %f seconds' % (func.__name__, t1-t0))
                return res
            except:
                logger.exception('Error in %s' % func.__name__)
                raise
        return wrapper
    return decorator

