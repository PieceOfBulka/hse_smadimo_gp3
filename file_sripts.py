import os
from logger_master import get_logger

log = get_logger('FILES')


def create_checkpoints_dir(name_of_dir = 'checkpoints'):
    os.makedirs(
        name_of_dir,
        exist_ok = True
    )
    
    log.info(f'Папка: {name_of_dir} успешно создана')
