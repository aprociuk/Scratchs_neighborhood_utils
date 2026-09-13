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
    
