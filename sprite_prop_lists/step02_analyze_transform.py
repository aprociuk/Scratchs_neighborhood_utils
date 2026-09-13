import os
import pandas as pd
import sqlite3


def sprite_prop_roadmap(gparams):
    
    # Connect to the SQLite database
    # Note: if the database did not exist, then this
    #       command would create it.
    conn = sqlite3.connect(os.path.join(params['sqlite3_dbs'],'scratchs_neighborhood.db'))
    cursor = conn.cursor()
    
    cursor.executescript('''
        drop table if exists sprite_prop_roadmap;
        create table sprite_prop_roadmap as
        select 
        from ;
    ''')
    
    superbowl_win_counts = pd.read_sql_query(
            "select * from sprite_prop_roadmap", conn
    )
    
