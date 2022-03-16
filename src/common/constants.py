import os

script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(script_dir))
result_path = project_root + '/result/'
print(result_path)

def get_result_path(dir):
    if not os.path.exists(result_path + dir):
        os.makedirs(result_path + dir)
    return result_path + dir