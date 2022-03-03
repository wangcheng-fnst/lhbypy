import os

result_path = '../../work/result/'

def get_result_path(dir):
    if not os.path.exists(result_path + dir):
        os.makedirs(result_path + dir)
    return result_path + dir