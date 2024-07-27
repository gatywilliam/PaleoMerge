from flask import Flask, jsonify, request
from paleo_utils import download_data, merge_data, predict_column
import pandas as pd
import pandasgui as pdg

app = Flask(__name__)

@app.route('/import')
def create_dataframe_service():
    try:
        # Get path string from query parameters
        app.path_to_local_data = request.args.get('path')
        print("Path:", app.path_to_local_data)
        df_dict = pd.read_excel(app.path_to_local_data, sheet_name=None, index_col=0)
        #print("df:", df_dict)

        if (df_dict == None):
            return {"status": 500, "message": 'Error creating dataframe.'}
        
        keys_list = []
        for key in df_dict.keys():
            print(key)
            keys_list.append(key)

        local_df = df_dict[keys_list[0]]
        local_df = local_df.sort_index()
        if keys_list[1] == 'metadata':
            app.metadata_df = df_dict[keys_list[1]]
        print(local_df.head())
        app.local_df = local_df
        if (len(keys_list) == 2):
            app.local_metadata_df = df_dict[keys_list[1]]
        print("Dataframe imported")
        return {"status": 200, "message": 'Dataframe created successfully.'}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error creating dataframe: {e}'}

@app.route('/update')
def update_data_service():
    try:
        remote_df = download_data()
        print('Downloading database data...')
        app.remote_df = remote_df.set_index('occurrence_no')
        print('Done downloading database data')
        return {"status": 200, "message": "Data merged successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error merging data: {e}'}

@app.route('/save-as')
def save_data_as_service():
    try:
        app.filepath = request.args.get('path')
        print("Path:", app.filepath)
        print("Saving data to:", app.filepath)
        writer = pd.ExcelWriter(app.filepath, engine='xlsxwriter')
        app.local_df.to_excel(writer, sheet_name='raw_data')
        app.metadata_df.to_excel(writer, sheet_name='metadata')
        #app.local_metadata_df.to_excel(writer, sheet_name='metadata')
        writer.close()
        print('Done saving data')
        return {"status": 200, "message": "Data saved successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error saving data: {e}'}

@app.route('/save')
def save_data_service():
    try:
        print("Saving data to:", app.path_to_local_data)
        # print("local_df:", app.local_df)
        writer = pd.ExcelWriter(app.path_to_local_data, engine='xlsxwriter')
        app.local_df.to_excel(writer, sheet_name='raw_data')
        app.local_metadata_df.to_excel(writer, sheet_name='metadata')
        writer.close()
        print('Done Saving data')
        return {"status": 200, "message": "Data saved successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error saving data: {e}'}

@app.route('/merge')
def merge_data_service():
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
    try:
        print('Predicting Data...')
        prediction_column = request.args.get('column')
        app.local_df, app.metadata_df, prediction_count = predict_column(app.local_df, prediction_column, app.metadata_df)
        print('Done Predicting')
        return {'status': 200, 'message':{prediction_column: prediction_count}}
    except Exception as e:
        print('Error', e)
        return {'status': 500, 'message': f'Error predicting data: {e}'}

@app.route('/pandas')
def open_pandas_service():
    try:
        # Show data in a GUI
        print("Showing data in a GUI...")
        gui = pdg.show(app.local_df)
        data = gui.get_dataframes()
        app.local_df = data[list(data.keys())[0]]
        #app.local_df.set_index('occurence_no')
        return {"status": 200, "message": "Data shown successfully."}
    except Exception as e:
        print("Error:", e)
        return{"status": 500, "message": f'Error opening PandasGUI: {e}'}

if __name__ == '__main__':
    create_dataframe_service()
