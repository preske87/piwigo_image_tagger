import datetime as dt
import os
import logging
import logging.handlers as handlers

logging.root.setLevel(logging.DEBUG)

max_log_size = 1024*1024*10
fh = handlers.RotatingFileHandler(os.path.join("log", "piwigo_image_tagger.log"), maxBytes=max_log_size, backupCount=2)
ch = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s -  %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

if len(logging.getLogger().handlers) == 0:
    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(ch)