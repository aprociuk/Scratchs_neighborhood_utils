import os
from _000_system_include.global_functions import global_parameters

def file_exists(mypath, myfiles):
    all_files_exist = True
    status_str = f"\n\nChecking location: {mypath}"
    
    for myfile in myfiles:
        file_exists = os.path.isfile(os.path.join(mypath, myfile))
        all_files_exist = all_files_exist and file_exists
        
        if file_exists:
            status_str += f"\n -- Found: {myfile}"
        else:
            status_str += f"\n -- Missing: {myfile}"
            
    return all_files_exist, status_str


def load_save_path(path=None):
    # Create buffer to store prior chosen folder
    # 1. Create file name
    params=global_parameters(report_paths=False)
    file_name = os.path.join(params['data_path'],".selected_file.txt")
    
    if path == None and os.path.isfile(file_name):
        # 2. Retrieve the string from the file
        with open(file_name, "r", encoding="utf-8") as file:
            path = file.read()
        return path
    elif path == None and not os.path.isfile(file_name):
        path = os.getcwd()
        # 2. Save the string to a file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(path)
        return path
    else:
        # 3. Save the string to a file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(path)

