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


def weave_scratch_list(names_file, values_file):
    status_str = "\n"

    namesdf=pd.read_csv(names_file, names=['parameter'])
    status_str += f"\nLoaded file:\n --{names_file} ({namesdf.size} records)"
    
    valuesdf=pd.read_csv(values_file, names=['value'])
    status_str += f"\nLoaded file:\n --{values_file} ({valuesdf.size} records)"
    
    if namesdf.size == valuesdf.size:
        weaved_df = pd.merge(namesdf, valuesdf, left_index=True, right_index=True)
        status_str += f"\nLOADED FILES SUCCESSFULLY WEAVED"
    else:
        status_str += f"\nLOADED FILES NOT WEAVED: Unequal record counts."
    
    return weaved_df, status_str

