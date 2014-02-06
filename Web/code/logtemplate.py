""" SHORTCUT FOR THE STANDARD LOG FORMAT THAT WE ALWAYS USE"""

import logging

LOG_LEVELS = {"debug":  logging.DEBUG,
              "info" : logging.INFO,
              "warning" : logging.WARNING,
              "critical" : logging.CRITICAL,
              "error" : logging.ERROR}

LOG_FORMAT_WITH_NAME = "%(asctime)s [%(name)s] [%(levelname)s] - %(message)s"
LOG_FORMAT_NONAME = "%(asctime)s [%(levelname)s] - %(message)s"

def get_log(name=None,
            level=None):
    # logger name (default is no name)
    if isinstance(name, (str, unicode)):
        log_format = LOG_FORMAT_WITH_NAME
    else:
        log_format = LOG_FORMAT_WITH_NONAME 
        name = 'log'

    # logging level (default is debug)
    level = level.lower()
    if level in LOG_LEVELS:
        log_level = LOG_LEVELS[level]
    else:
        log_level = logging.DEBUG

    print name, level, log_level
    # set it up
    logging.basicConfig(level=log_level,
                        format=log_format,
                        datefmt='%y-%m-%d %H:%M:%S')
    return logging.getLogger(name)
    
