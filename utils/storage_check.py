import os

def does_shelve_exist(save_file):
    files = os.listdir('.')
    for file in files:
        if file.startswith(save_file):
            return True
    return False

def remove_shelve(save_file):
    files = os.listdir('.')
    for file in files:
        if file.startswith(save_file):
            os.remove(file)