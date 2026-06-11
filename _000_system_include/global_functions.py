import pandas as pd
import sqlite3

# for plotting example below
import seaborn as sns
import matplotlib.pyplot as plt


# os module used to interact woth operating system
#    (e.g. change paths, environment variables, etc.)
import os


def print_all(prt_obj):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(prt_obj)


def global_parameters(report_paths=True):
    """
    This function defines parameters used throughout modules (e.g. paths).
    It also creates the paths for dataframe (parquet file) storage for the
    given analysis and, more broadly, the SQLite database
    storage path for the repository, if these do not already exist.  If 
    the repository folder is stored one or more layers within a folder named
    "program" or "programs", then an analogous folder tree will be created 
    under a folder named "data" at the same level as the "program(s)" folder.  
    If the "program(s)" folder does not exist, then the data will be stored 
    at the appropriate level under the same repo/analysis folders where the code
    is stored.  
    
    Args:
        report_paths (bool): If True, print all of the parameter labels
                             and values.  If False, suppress printing.  
                             Defaults to True if unspecified.
        
    Returns:
        Dictionary of parameter labels and their values.  If the dictionary
        is stored in variable p, then individual parameters can be accessed 
        with value = p['label'].  For example:
        
        # Call function to access dataframe storage path:
        p = global_parameters()

        # Get path designated for storing dataframes as parquet files:
        dpath = g['data_path']
    """
        
    repo_name='Scratchs_neighborhood_utils'
    
    prog_path = os.getcwd()
    prog_base = prog_path.split(repo_name)[0]
    repo_path = os.path.join(prog_base,repo_name)
    data_base=prog_base.replace('program','data')
    
    sqlite3_dbs = os.path.join(data_base,'sqlite3_dbs')
    os.makedirs(sqlite3_dbs, exist_ok=True)
    
    data_path=prog_path.replace('program','data')
    os.makedirs(data_path, exist_ok=True)
    
    if report_paths:
        print("\nprog_path: ")
        print(prog_path)
        
        print("\nprog_base: ")
        print(prog_base)
        
        print("\nrepo_path: ")
        print(repo_path)
        
        print("\ndata_base: ")
        print(data_base)
        
        print("\nsqlite3_dbs: ")
        print(sqlite3_dbs)
        
        print("\ndata_path: ")
        print(data_path)
        
        print('\n\n')
    
    # Define parameters
    params = {
        "prog_path": prog_path,
        "repo_path": repo_path,
        "data_base": data_base,
        "data_path": data_path,
        "sqlite3_dbs": sqlite3_dbs
    }
    
    return params




def pull_tokens(token_file: str):
    """
    Pulls the keys from a token list file

    Parameters:
        token_file (str): Two column list of tokens.  
            First column is a human readable label describing 
            the token source.  Second column is the associated
            token.
            
    Returns:
        The list of tokens stored in a series with the first 
        column label stored as the row index.
    """
    tokens_df = pd.read_csv(token_file, header=None)
    tokens = tokens_df.set_index(0)[1]
    return tokens


def freq(df=pd.DataFrame(), sql_tbl=None, sql_db=None, group_by=None, print_all=False):
        
    _freq=None
    if not df.empty:
        if group_by==None:
            _freq = len(df)
            print(f"\nNumber of rows: {_freq}\n")
        else:
            _freq = df.groupby(group_by).size().reset_index(name='Count')
            _freq['Percent'] = _freq['Count'] / len(df) * 100
            print(_freq)
    elif sql_tbl != None and sql_db != None:
        if group_by==None:
            _sql_str=f""" select count(*) as Total_Count
                          from {sql_tbl};
                      """
        else:
            _sql_str=f""" select a.*,
                                 cast(a.Count as real)/b.Total_Count * 100 as Percent
                                 from (
                                         select {group_by},
                                                count(*) as Count
                                         from {sql_tbl}
                                         group by {group_by}
                                         order by {group_by}
                                 ) a
                                 left join (
                                         select count(*) as Total_Count
                                         from {sql_tbl}
                                 ) b
                                 on 1;
                      """
        _freq = pd.read_sql_query(_sql_str, sql_db)
        
        if print_all == True:
            print_all(_freq)
        else:
            print(_freq)
    else:
        print("\nNo dataframe or table specified\n")
    
    return _freq


def sql_table_info(info_type='info', sql_tbl=None, sql_db=None, vars=None, *argc, **argv):
    
    info_type=info_type.upper()
    
    _freq=None
    if sql_tbl != None and sql_db != None:
        if vars==None:
            _sql_str=f"select * from {sql_tbl};"
        else:
            _sql_str=f"select {vars} from {sql_tbl};"
        
        if info_type == 'INFO':
            _freq = pd.read_sql_query(_sql_str, sql_db).info(*argc, **argv)
        elif info_type == 'HEAD':
            _freq = pd.read_sql_query(_sql_str, sql_db).head(*argc, **argv)
        elif info_type == 'DESC':
            _freq = pd.read_sql_query(_sql_str, sql_db).describe(*argc, **argv)
        
        print(_freq)
    else:
        print("\nNo sql table or database connection specified\n")
    
    return _freq


def draw_bar_graph(fig_file_name=None, 
                   figure_size=(8, 6),
                   title=None, 
                   xlabel=None, 
                   ylabel=None, 
                   *args, 
                   **kwargs
                  ):
    
    # Get paths
    params = global_parameters(report_paths=False)
    
    # Create the bar plot
    plt.figure(figsize=figure_size) # Optional: adjust figure size
    ax = sns.barplot(*args, **kwargs)
    
    # Customize and display
    if title != None:
        plt.title(title)
    if xlabel != None:
        plt.xlabel(xlabel)
    if ylabel != None:
        plt.ylabel(ylabel)
    
    plt.show()
    
    # Access the Figure object via the axes and save
    fig = ax.figure

    if fig_file_name != None:
        fig.savefig(os.path.join(params['prog_path'],fig_file_name))
    
    # return the figure handle in case anyone wants to use it
    # outside of this function
    return fig


def draw_cat_graph(fig_file_name=None, 
                   title=None, 
                   legend_title=None,
                   xlabel=None, 
                   ylabel=None, 
                   *args, 
                   **kwargs
                  ):
    
    # Get paths
    params = global_parameters(report_paths=False)
    
    # Create the bar plot
    g = sns.catplot(*args, **kwargs)
    
    # Optional: Further customization
    g.despine(left=True)

    # Customize and display
    if title != None:
        g.fig.suptitle(title)
    if legend_title != None:
        g.legend.set_title(legend_title)
    if xlabel != None and ylabel != None:
        g.set_axis_labels(xlabel, ylabel)

    if fig_file_name != None:
        g.savefig(os.path.join(params['prog_path'],fig_file_name))
    
    plt.show()
    
    # Optional: Close the plot window if you are not displaying it, 
    # especially important in some environments like Jupyter notebooks
    # to prevent blank images if not saved before plt.show().
    #plt.close(g.fig)
    
    return g




def draw_pie_chart(fig_file_name=None, 
                   df=pd.DataFrame(),
                   category_column=None,
                   value_column=None,
                   figure_size=(6, 6),
                   title=None, 
                   *args, 
                   **kwargs
                  ):
    
    # Get paths
    params = global_parameters(report_paths=False)
    
    if (not df.empty) or category_column == None or value_column == None:
        # To plot a pie chart, the data must be a Series or a single column
        # and it is helpful to set the labels as the index
        series_data = df.set_index(category_column)[value_column]
        
        # 2. Create the pie chart
        plt.figure(figsize=figure_size) # Optional: adjust figure size for a better look
        ax = series_data.plot.pie(autopct='%.1f%%', startangle=90, *args, **kwargs)
        
        # 3. Ensure the plot is circular
        plt.axis('equal') # Equal aspect ratio ensures the pie chart is circular
        
        # 4. Add a title and display the plot
        plt.title(title)
        plt.show()
        
        # Pull figure handle
        fig = ax.figure
        
        # Access the Figure object via the axes and save
        if fig_file_name != None:
            fig_path=os.path.join(params['prog_path'],fig_file_name)
            fig.savefig(fig_path)
        
        return fig
    else:
        print("\nData for plot missing or incomplete\n")
        return None