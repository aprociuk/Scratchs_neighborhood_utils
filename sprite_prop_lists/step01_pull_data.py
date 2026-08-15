import os
import pandas as pd
from datetime import datetime
from _000_system_include.global_functions import global_parameters


def build_prop_tables(mypath, myfiles):
    all_files_exist, status_str = file_exists(mypath, myfiles)
    if all_files_exist:
        # Build prop list
        weaved_prop, status_str2 = weave_scratch_list(
            os.path.join(mypath,myfiles[0]), 
            os.path.join(mypath,myfiles[1])
        )
        status_str += status_str2


def build_sprite_tables(mypath, myfiles):
    all_files_exist, status_str = file_exists(mypath, myfiles)
    if all_files_exist:
        # Build sprite list
        weaved_sprite, status_str2 = weave_scratch_list(
            os.path.join(mypath,myfiles[0]), 
            os.path.join(mypath,myfiles[1])
        )
        status_str += status_str2
        print(status_str)
        print(weaved_sprite)
        
        if not weaved_sprite.empty:
            # Create table with sprite_id, keyword and value columns
            weaved_sprite['sprite_id']=weaved_sprite['parameter'].str.partition("-")[0]
            weaved_sprite['keyword']=weaved_sprite['parameter'].str.partition("-")[1]
            sprite_and_uber = weaved_sprite[['sprite_id','keyword','value']]
            print("\nsprite_and_uber:")
            print(sprite_and_uber)
            
            # Split into uber sprite and plain sprite tables
            uber_sprite_list=(
                sprite_and_uber[ sprite_and_uber['sprite_id'].str.contains(r"^u[0-9]+", na=False) ]
                .rename(columns = {'sprite_id':'uber_id'})
            )
            print("\nuber_sprite_list:")
            print(uber_sprite_list)
            plain_sprite_list=sprite_and_uber[ 
                sprite_and_uber['sprite_id'].str.contains(r"^[0-9]+", na=False) 
            ]
            print("\nplain_sprite_list:")
            print(plain_sprite_list)
            
            # Split uber sprite table into sprite_order/sprite_id and layer tables
            uber_layers = reshape_to_wide(uber_sprite_list, 'layer', 'layer')
            print("\nuber_layers:")
            print(uber_layers)
        
            uber_sprite_ids = reshape_to_wide(
                uber_sprite_list, "sprite_id_", 'sprite_id', rename_keyword='sprite_order'
            )
            print("\nuber_sprite_ids:")
            print(uber_sprite_ids)
            
            # Create uber - sprite - layer look up (uber_id, layer, sprite_order, sprite_id)
            uber_xwalk = pd.merge(uber_layers, uber_sprite_ids, how='inner', on=['uber_id'], sort=False)
            print("\nuber_xwalk:")
            print(uber_sprite_ids)

            # Save uber_xwalk to parquet and sqlite
            
            # Split plain sprite table into:
            #   1. sprite first/last costume table 
            #   2. sprite alternate costume table
            #   3. sprite other parameters tables
            sprite_first_costume = reshape_to_wide(plain_sprite_list, r"^first.*costume$", 'first_costume')
            print("\nsprite_first_costume:")
            print(sprite_first_costume)

            sprite_last_costume = reshape_to_wide(plain_sprite_list, r"^last.*costume$", 'last_costume')
            print("\nsprite_last_costume:")
            print(sprite_last_costume)

            # Create sprite - prop look ups (wide costume format)
            sprite_costumes_main = pd.merge(sprite_first_costume, sprite_last_costume, how='inner', on=['sprite_id'], sort=False)

            # Save sprite_costumes_main to parquet/sql


            # Create sprite ranges crosswalk (wide - min, max) for 
            # landmark 0/1 alternate props.  For landmark 1, the the
            # single position will bestored as a min and max value to 
            # make relation matching code more fluid.  


def reshape_to_wide(indf, search_for, rename_to, rename_keyword=None, regex=True):
    outdf = (
        indf[ indf['keyword'].str.contains(search_for, na=False, regex=regex) ]
        .rename(columns={'value':rename_to})
    )
    if rename_keyword != None:
        outdf[rename_keyword] = outdf['keyword'].str.partition(search_for)[0]
    outdf = outdf.drop(columns='keyword')
    
    return outdf


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
        weaved_df = pd.DataFrame([])
        status_str += f"\nLOADED FILES NOT WEAVED: Unequal record counts."
    
    return weaved_df, status_str


def archive_files(mypath, myfiles):
    status_str = "\n"
    
    # Get current date and time
    now = datetime.now()
    # Format as a readable string (e.g., "2026-07-11 12:35:00")
    mysubfldr = now.strftime("%Y%m%d_%Hh%Mm%Ss")
    
    # Determine if at least one of the files exists (for archiving purposes)
    one_file_exists = False
    for myfile in myfiles:
        one_file_exists = one_file_exists or os.path.isfile(os.path.join(mypath, myfile))
    
    if one_file_exists:
        arch_path = os.path.join(mypath, mysubfldr)
        os.path.mkdirs(arch_path)
    
    for myfile in myfiles:
        if os.path.isfile(os.path.join(mypath, myfile)):
            os.rename(
                os.path.join(mypath, myfile), 
                os.path.join(arch_path, myfile)
            )
            status_str += f"\nFound file {myfile}: archived to subfolder {mysubfldr}"
    
    return status_str


def write_files(mypath, mydfs, myfiles):
    status_str = archive_files(mypath, myfiles)
    if len(mydfs) == lent(myfiles):
        for n in len(mydfs):
            mydfs[n].to_csv(
                path_or_buf=os.path.join(mypath, myfiles[n]), 
                header=False, 
                index=False
            )
            status_str += f"\nWrote {myfiles[n]}"
    else:
        status_str += f"\nINTERNAL ERROR: Number of lists ({len(mydfs[n])}) and number of files ({len(myfiles[n])}) differ.  No files written."
        
    return status_str


def split_scratch_list(scratch_list, mypath, names_file, values_file):
    namesdf=scratch_list[['parameter']]    
    valuesdf=scratch_list[['value']]
    status_str = write_files(mypath, [namesdf, valuesdf], [names_file, values_file])
    return status_str
