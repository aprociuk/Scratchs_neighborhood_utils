import os
import pandas as pd
import sqlite3


def create_sprite_prop_roadmap(params):
    
    # Connect to the SQLite database
    # Note: if the database did not exist, then this
    #       command would create it.
    conn = sqlite3.connect(os.path.join(params['sqlite3_dbs'],'scratchs_neighborhood.db'))
    cursor = conn.cursor()
    
    cursor.executescript('''
        drop table if exists sprite_prop_roadmap;
        
        create table sprite_prop_roadmap as
        select a.uber_id,
               a.sprite_id,
               c.prop_id,
               c.value as costume_name
        from uber_xwalk a
        inner join ( 
            select * 
            from sprite_costumes_main
            where first_costume is not NULL and 
                  last_costume is not NULL
        ) b
        on a.sprite_id = b.sprite_id
        inner join (
            select *
            from plain_prop_list
            where keyword like 'costume_name%'
        ) c
        on b.first_costume <= c.prop_id and 
           c.prop_id <= b.last_costume
        order by a.uber_id,
                 a.sprite_id,
                 c.prop_id,
                 c.value;
    ''')
    
    sprite_prop_roadmap = pd.read_sql_query(
            "select * from sprite_prop_roadmap", conn
    )
    sprite_prop_roadmap.to_parquet(
        os.path.join(params['data_path'],'sprite_prop_roadmap.parquet'), 
        index=False
    )
    status_str = "\nSprite-prop roadmap reproduced."
    return status_str, sprite_prop_roadmap


def compare_dfs(df_a, df_b, key_vars, diff_var):
    if isinstance(diff_var, list):
        # If diff_var is a list then return error message and 
        # empty df (diff_var needs to be a single variable)
        status_str = f"\nINTERNAL ERROR: Unable to compare.  {diff_var} is not a single variable."
        return pd.DataFrame()
    else:
        # Create list of all relevant variables
        if isinstance(key_vars, list):
            all_vars = key_vars
            all_vars.append(diff_var)
        else:
            all_vars = [key_vars, diff_var]
        
        # Deduplicate dfs
        df_a_ddup = df_a[[all_vars]].drop_duplicates()
        df_b_ddup = df_b[[all_vars]].drop_duplicates()
        
        # Create table A and table B variable to compare
        df_a_ddup[f"Table A: {diff_var}"] = df_a_ddup[diff_var]
        df_b_ddup[f"Table B: {diff_var}"] = df_b_ddup[diff_var]
        
        # Merge df_a to df_b by key_vars
        # Drop original diff_var
        df_diff_pre = pd.merge(
            df_a_ddup, df_b_ddup,
            on = key_vars,
            how = "outer"
        ).drop(columns=diff_var)
        
        # Keep only differences
        df_diff = df_diff_pre[
            ( 
                (df_diff_pre[f"Table A: {diff_var}"].isna()) 
                &
                (~df_diff_pre[f"Table B: {diff_var}"].isna()) 
            ) |
            ( 
                (~df_diff_pre[f"Table A: {diff_var}"].isna()) 
                &
                (df_diff_pre[f"Table B: {diff_var}"].isna()) 
            ) |
            (df_diff_pre[f"Table A: {diff_var}"] != df_diff_pre[f"Table B: {diff_var}"])
        ]
    
    # Return table of differences
    return status_str, df_diff


