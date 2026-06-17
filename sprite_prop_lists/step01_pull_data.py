import os

def file_exists(mypath, myfiles):
    all_files_exist = True
    for myfile in myfiles:
        file_exists = os.path.isfile(os.path.join(mypath, myfile))
        all_files_exist = all_files_exist and file_exists
    return all_files_exist

