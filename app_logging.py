import queue
import logging
from logging import handlers
import constants


root_logger: logging.Logger = logging.getLogger(name=constants.LOG_NAME)


def initiate_log(config: dict) -> handlers.QueueListener:
    # Initiate logging
    que = queue.Queue(-1)
    queue_handler = handlers.QueueHandler(que)
    handler = logging.FileHandler(config['General']['log_file'], mode='w', encoding='utf-8')
    log_listener = handlers.QueueListener(que, handler)
    root_logger.setLevel(level=logging.INFO)
    root_logger.addHandler(queue_handler)
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s: %(message)s')
    handler.setFormatter(log_formatter)
    log_listener.start()
    root_logger.info('Logging started for application!')
    return log_listener


def get_logger() -> logging.Logger:
    return root_logger
