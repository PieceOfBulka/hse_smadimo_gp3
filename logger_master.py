import os
import logging
from datetime import datetime


base_dir = os.path.dirname(os.path.abspath(__file__))
logi_dir = os.path.join(base_dir, 'LOGI')
os.makedirs(
        os.path.join(base_dir, 'LOGI'),
        exist_ok = True
)

log_debug_file_name = os.path.join(logi_dir, f'debug_time_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
log_info_file_name  = os.path.join(logi_dir, f'info_time_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')


# из статьи: https://sky.pro/wiki/media/kak-rabotat-s-logirovaniem-v-python/
format = logging.Formatter(
    '%(asctime)s – %(name)s – %(levelname)s – %(message)s',
    datefmt = "%Y-%m-%d_%H-%M-%S"
)

debug_handler = logging.FileHandler(log_debug_file_name, encoding='utf-8')
debug_handler.setFormatter(format)
debug_handler.setLevel(logging.DEBUG)

info_handler = logging.FileHandler(log_info_file_name, encoding='utf-8')
info_handler.setFormatter(format)
info_handler.setLevel(logging.INFO)

def get_logger(name_obj):
    logger = logging.getLogger(name_obj)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        logger.addHandler(debug_handler)
        logger.addHandler(info_handler)

    return logger
