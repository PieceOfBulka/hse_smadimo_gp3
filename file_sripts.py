import os
from logger_master import get_logger

log = get_logger('FILES')


def create_checkpoints_dir(name_of_dir = 'checkpoints'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, name_of_dir)
    os.makedirs(
        path,
        exist_ok = True
    )
    
    log.info(f'Папка: {name_of_dir} успешно создана')
    
    return path
