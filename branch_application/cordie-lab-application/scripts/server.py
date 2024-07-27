import subprocess
from flask import Flask, jsonify, request
from paleo_utils import download_data, merge_data, predict_column
import pandas as pd
import pandasgui as pdg
import os
from gui import open_gui

app = Flask(__name__)

@app.route('/import')
def create_dataframe_service():
    """
    Creates a dataframe from imported excel file
    """
    try:
        # Get path string from query parameters
        app.path_to_local_data = request.args.get('path')
        print("Path:", app.path_to_local_data)
        df_dict = pd.read_excel(app.path_to_local_data, sheet_name=None, index_col=0)
        # If not dataframes in excel throw error
        if (df_dict == None):
            return {"status": 500, "message": 'Error creating dataframe.'}
        
        keys_list = []
        # Print the found dataframes
        for key in df_dict.keys():
            print(key)
            keys_list.append(key)

        local_df = df_dict[keys_list[0]]
        local_df = local_df.sort_index()
        # If metadata is in the imported file, set server's metadata to that
        if keys_list[1] == 'metadata':
            app.metadata_df = df_dict[keys_list[1]]
        app.local_df = local_df
        print("Dataframe imported")
        return {"status": 200, "message": 'Dataframe created successfully.'}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error creating dataframe: {e}'}

@app.route('/update')
def update_data_service():
    """
    Downloads newest data from Paleobiological Database and puts it in a dataframe
    """
    try:
        remote_df = download_data()
        print('Downloading database data...')
        app.remote_df = remote_df.set_index('occurrence_no')
        print('Done downloading database data')
        return {"status": 200, "message": "Data updated successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error downloading data: {e}'}

@app.route('/save-as')
def save_data_as_service():
    """
    Saves a file as the provided path
    """
    try:
        app.path_to_local_data = request.args.get('path')
        print("Saving data to:", app.path_to_local_data)
        writer = pd.ExcelWriter(app.path_to_local_data, engine='xlsxwriter')
        app.local_df.to_excel(writer, sheet_name='raw_data')
        app.metadata_df.to_excel(writer, sheet_name='metadata')
        writer.close()
        print('Done saving data')
        return {"status": 200, "message": "Data saved successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error saving data: {e}'}

@app.route('/save')
def save_data_service():
    """
    Saves the file as the same path
    """
    try:
        print("Saving data to:", app.path_to_local_data)
        writer = pd.ExcelWriter(app.path_to_local_data, engine='xlsxwriter')
        app.local_df.to_excel(writer, sheet_name='raw_data')
        app.metadata_df.to_excel(writer, sheet_name='metadata')
        writer.close()
        print('Done Saving data')
        return {"status": 200, "message": "Data saved successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error saving data: {e}'}

@app.route('/merge')
def merge_data_service():
    """
    Merges the imported dataframe with the newest Paleobiological Database data
    """
    try:
        print('Merging Data...')
        app.local_df, app.metadata_df, merge_info = merge_data(app.remote_df, app.local_df)
        print('Done Merging Data')
        return {'status': 200, "message": {'Local Overrides': merge_info[0], 'Remote Overrides': merge_info[1], 'Added Columns': merge_info[2]}}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error merging data: {e}'}

@app.route('/predict')
def predict_data_service():
    """
    Makes Predictions on the given columns
    """
    try:
        print('Predicting Data...')
        prediction_column = request.args.get('column')
        print('Predicting', prediction_column)
        app.local_df, app.metadata_df, prediction_count, copy_count, low_confidences = predict_column(app.local_df, prediction_column, app.metadata_df)
        print('Done Predicting')
        return {'status': 200, 'message':{prediction_column: {'Predictions': prediction_count, 'Copied': copy_count, 'Low Confidences': low_confidences}}}
    except Exception as e:
        print('Error', e)
        return {'status': 500, 'message': f'Error predicting data: {e}'}

@app.route('/pandas')
def open_pandas_service():
    """
    Saves data to file, then starts seperate script for pandas gui. This is done to increase stability of pandasGUI
    """
    save_data_service()
    # result = os.system('python gui.py \'{0}\''.format(app.path_to_local_data))
    # if result == 0:
    # open_gui = subprocess.Popen(['python', 'gui.py', app.path_to_local_data])
    open_gui(app.path_to_local_data)
    return {"status": 200, "message": "Data shown successfully."}
    # else:
    return{"status": 500, "message": 'Error opening PandasGUI'}

@app.route('/pandas-open')
def open_pandas_service_path():
    """
    Opens pandas gui in seperate script without first saving file
    """
    app.path_to_local_data = request.args.get('path')
    result = os.system('gui.py {0}'.format(app.path_to_local_data))
    if result == 0:
        return {"status": 200, "message": "Data shown successfully."}
    else:
        return{"status": 500, "message": 'Error opening PandasGUI'}

if __name__ == '__main__':
    create_dataframe_service()
