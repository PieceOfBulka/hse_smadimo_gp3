import os

def create_checkpoints_dir(name_of_dir = 'checkpoints'):
    os.makedirs(
        name_of_dir,
        exist_ok = True
    )
    
