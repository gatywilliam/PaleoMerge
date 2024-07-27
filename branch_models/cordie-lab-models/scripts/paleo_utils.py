import requests
from io import StringIO
import pandas as pd

def download_data():
    # Make HTTP request to Paleobiology database API
    print("Downloading data from Paleobiology database...")
    endpoint = "http://paleobiodb.org/data1.2/occs/list.csv?taxon_reso=lump_genus&idqual=certain&pres=regular&max_ma=514&min_ma=477.7&show=class,loc,paleoloc,refattr,acconly"
    response = requests.get(endpoint)

    # Convert text response to csv in runtime
    print("Converting data to csv...")
    data = StringIO(response.text)

    # Put data into a dataframe
    print("Putting data into a dataframe...")
    df = pd.read_csv(data)
    print("Done!")
    return df

def predict_column(df, test_output, metadata_df):
    prediction_count = 0
    unique_column = {}
    if test_output in df.columns:
        for i in df.index:
            if df.loc[i,'accepted_name'] in unique_column and df.loc[i, test_output] not in unique_column[df.loc[i, 'accepted_name']] and not pd.isna(df.loc[i, test_output]):
                unique_column[df.loc[i, 'accepted_name']].append(df.loc[i, test_output])
            elif df.loc[i, 'accepted_name'] not in unique_column and not pd.isna(df.loc[i, test_output]):
                unique_column[df.loc[i, 'accepted_name']] = [df.loc[i, test_output]]
        for i in df.index:
            if pd.isna(df.loc[i, test_output]) and df.loc[i, 'accepted_name'] in unique_column.keys():
                if len(unique_column[df.loc[i, 'accepted_name']]) == 1:
                    df.loc[i, test_output] = unique_column[df.loc[i, 'accepted_name']][0]
                    prediction_count += 1
                    metadata_df.loc[i, test_output] = 2
            elif not pd.isna(df.loc[i, test_output]) and df.loc[i, 'accepted_name'] in unique_column.keys():
                metadata_df.loc[i, test_output] = 1
    else:
        raise Exception('Prediction column does not exist')
    return df, metadata_df, prediction_count

    

def merge_data(df, df_cordie):
    """
    Merges 2 dataframes together removing any identical values and if there are any discrepencies
    assumes the 'df_cordie' is correct unless null
    df_cordie is modified dataframe
    df is dataframe straight from paleobiology database
    """
    pd.set_option('display.max_columns', None)
    differences = []
    database_overrides = 0
    cordie_overrides = 0
    added_columns = list(set(df.columns) - set(df_cordie.columns))
    metadata_df = pd.DataFrame(index=df.index)
    for column in df.columns:
        if column in df_cordie:
            for i in df.index:
                if i in df_cordie.index:
                    if df.loc[i, column] != df_cordie.loc[i, column] and not pd.isna(df_cordie.loc[i, column]):
                        if column not in differences:
                            differences.append(column)
                        df.loc[i, column] = df_cordie.loc[i, column]
                        cordie_overrides += 1
                        metadata_df.loc[i, column] = 1
                    elif df.loc[i, column] != df_cordie.loc[i, column] and pd.isna(df_cordie.loc[i, column]) and not pd.isna(df.loc[i, column]):
                        df_cordie.loc[i, column] = df.loc[i, column]
                        database_overrides += 1
                        #metadata_df.loc[i, column] = 0
                    #elif df.loc[i, column] == df_cordie.loc[i, column]:
                        #metadata_df.loc[i, column] = 0
        #else:
            #metadata_df.loc[:, column] = 0
    same = []
    for column in df_cordie.columns:
        if column not in differences and column in df.columns:
            same.append(column)
            #metadata_df.loc[:, column] = 0
    df_cordie = df_cordie.drop(columns = differences)
    df_cordie = df_cordie.drop(columns = same)
    print('Cordie overrides:', cordie_overrides)
    print('Database overrides', database_overrides)
    print('Added columns', added_columns)
    new_df = pd.merge(df, df_cordie, how="left", on="occurrence_no")
    return new_df, metadata_df, [cordie_overrides, database_overrides, added_columns]
