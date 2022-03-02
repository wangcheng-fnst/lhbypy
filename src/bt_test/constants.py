import os

result_path = '../../work/result/'

def get_result_path():
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path