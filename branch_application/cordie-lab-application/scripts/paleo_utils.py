import requests
from io import StringIO
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier as RFC
import json
import numpy as np
import warnings

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
    """
    Predicts all null values in the given column
    @param test_output: column being predicted
    @param df: the dataframe predictions are being based on
    @param metadata_df: metadata for the provided dataframe
    """
    loaded_model = ''
    # Changes the input for the ML model based on what column is being predicted
    if test_output == 'skeletal_material':
        test_output = 'Skeletal Material'
        loaded_model = joblib.load('skeletal_material_model.joblib')
        predictive_columns = ['early_interval', 'max_ma', 'min_ma', 'phylum', 'class', 'order', 'family', 'cc', 'paleolng', 'paleolat', 'geoplate']
    elif test_output == 'bin_interval':
        test_output = 'Bin Interval'
        loaded_model = joblib.load('bin_interval_model.joblib')
        predictive_columns = ['early_interval', 'max_ma', 'min_ma', 'cc', 'paleolng', 'paleolat', 'geoplate']
    # Input label encodings for models
    with open('label_and_feature_encodings.json', 'r') as f:
        encoding_reader = json.load(f)
    with open('write_encodings.json', 'r') as f:
        encoding_maker = json.load(f)
    
    prediction_count = 0
    copy_count = 0
    unique_column = {}
    low_confidences = {}
    print(df.columns)
    if test_output in df.columns:
        # Makes the lookup table
        for i in df.index:
            if df.loc[i,'accepted_name'] in unique_column and df.loc[i, test_output] not in unique_column[df.loc[i, 'accepted_name']] and not pd.isna(df.loc[i, test_output]):
                unique_column[df.loc[i, 'accepted_name']].append(df.loc[i, test_output])
            elif df.loc[i, 'accepted_name'] not in unique_column and not pd.isna(df.loc[i, test_output]):
                unique_column[df.loc[i, 'accepted_name']] = [df.loc[i, test_output]]
        # If prediction column not in metadata, adds it
        if test_output not in metadata_df.columns:
            metadata_df[test_output] = np.nan
        # Starts prediction for all that don't have metadata
        for i in df[metadata_df[test_output].isnull()].index:
            # If no value and in the lookup table, change to that
            if pd.isna(df.loc[i, test_output]) and df.loc[i, 'accepted_name'] in unique_column.keys() and len(unique_column[df.loc[i, 'accepted_name']]) == 1:
                df.loc[i, test_output] = unique_column[df.loc[i, 'accepted_name']][0]
                copy_count += 1
                metadata_df.loc[i, test_output] = 'copy'                    
            # If value, just change metadata to say its local
            elif not pd.isna(df.loc[i, test_output]):
                metadata_df.loc[i, test_output] = 'local'
            # If no value and uncrecognized accepted_name, make prediction
            elif pd.isna(df.loc[i, test_output]) and loaded_model != '':
                pred, prob = predict_row(df.loc[i, predictive_columns], predictive_columns, loaded_model, encoding_reader, encoding_maker, test_output)
                prediction_count += 1
                df.loc[i, test_output] = pred
                metadata_df.loc[i, test_output] = prob[0]
                if prob[0] <= .75:
                    low_confidences[i] = {test_output: prob[0]}

    else:
        raise Exception('Prediction column does not exist')
    return df, metadata_df, prediction_count, copy_count, low_confidences

def predict_row(row, columns, model, encoding_reader, encoding_maker, predict_column):
    """
    Predicts the output of a single row of data
    @param row: the row being predicted
    @param columns: the predictive columns to be used
    @param model: the model being used to create the predictions
    @param encoding_reader: tool used to read the encodings
    @param encoding_maker: tool used to convert the data to encodings
    @param predict_column: the column being predicted
    """
    warnings.filterwarnings("ignore")
    # Converts the data to encodings
    for column in columns:
        # If column is categorical
        if column not in ['max_ma', 'min_ma', 'paleolng', 'paleolat']:
            try:
                row[column] = encoding_maker[column][row[column]]
            except:
                # if encoding does not exist, make a new one
                encoding_maker[column][row[column]] = max(encoding_maker[column].values())
                row[column] = encoding_maker[column][row[column]]
    #reshape row for model
    row = np.asarray(row).reshape(1, -1)
    # make prediction
    pred = model.predict(row)
    # get confidence of prediction
    pred_confidence = model.predict_proba(row)
    # return unencoded prediction and confidence
    return encoding_reader[predict_column][str(pred[0])], pred_confidence[0,pred]
    

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
                        metadata_df.loc[i, column] = 'local'
                    elif df.loc[i, column] != df_cordie.loc[i, column] and pd.isna(df_cordie.loc[i, column]) and not pd.isna(df.loc[i, column]):
                        df_cordie.loc[i, column] = df.loc[i, column]
                        database_overrides += 1
    same = []
    for column in df_cordie.columns:
        if column not in differences and column in df.columns:
            same.append(column)
    df_cordie = df_cordie.drop(columns = differences)
    df_cordie = df_cordie.drop(columns = same)
    print('Cordie overrides:', cordie_overrides)
    print('Database overrides', database_overrides)
    print('Added columns', added_columns)
    new_df = pd.merge(df, df_cordie, how="left", on="occurrence_no")
    return new_df, metadata_df, [cordie_overrides, database_overrides, added_columns]
