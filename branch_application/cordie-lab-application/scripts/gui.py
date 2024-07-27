import pandasgui as pdg
import pandas as pd
import sys

def open_gui(path):
    # Read passed in file
    print('Reading File')
    df_dict = pd.read_excel(path, sheet_name=None, index_col=0)
    print('File Read')
    
    #Decipher metadata and data
    keys_list = []
    for key in df_dict.keys():
        keys_list.append(key)
    if keys_list[1] == 'metadata':
        metadata_df = df_dict[keys_list[1]]

    local_df = df_dict[keys_list[0]]

    print("Showing data in a GUI...")
    gui = pdg.show(local_df, metadata_df)
    data = gui.get_dataframes()
    print('Checking for changes...')
    gui_df = data[list(data.keys())[0]]
    diff = local_df.compare(gui_df)
    # Change local copy of dataframe and metadata to reflect changes
    if len(diff.index) != 0:
        for i in diff.index:
            for x in range(len(diff.loc[i])):
                if x % 2 == 1 and local_df.loc[i, diff.columns[x][0]] != gui_df.loc[i, diff.columns[x][0]] and not (pd.isna(gui_df.loc[i, diff.columns[x][0]]) and pd.isna(local_df.loc[i, diff.columns[x][0]])):
                    local_df.loc[i, diff.columns[x][0]] = diff.loc[i][x]
                    metadata_df.loc[i, diff.columns[x][0]] = 'local'
    print('Done Checking for changes')
    if len(diff.index) != 0:
        print("Saving data to:", path)
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        local_df.to_excel(writer, sheet_name='raw_data')
        metadata_df.to_excel(writer, sheet_name='metadata')
        print('Data Saved')
        writer.close()

if __name__ == '__main__':
    open_gui()