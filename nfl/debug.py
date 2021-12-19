import logging
logger = logging.getLogger('')

def log(text):
	logger.debug(text)

def warning(text):
	logger.warning(text)

def error(text):
	logger.error(text)

def info(text):
	logger.info(text)
