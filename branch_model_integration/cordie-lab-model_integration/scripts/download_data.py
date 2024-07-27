import requests
from io import StringIO
import pandas as pd

# TODO: Add error handling
def download_data():
    # Make HTTP request to Paleobiology database API
    print("Downloading data from Paleobiology database...")
    endpoint = "http://paleobiodb.org/data1.2/occs/list.csv?taxon_reso=lump_genus&idqual=certain&pres=regular&max_ma=514&min_ma=477.7&show=full"
    response = requests.get(endpoint)

    # Convert text response to csv in runtime
    print("Converting data to csv...")
    data = StringIO(response.text)

    # Put data into a dataframe
    print("Putting data into a dataframe...")
    df = pd.read_csv(data)
    

    # TODO: Not currently working
    # replace all equal signes at the beginning of a cell with a space and an equal sign
    # print("Replacing equal signes...")
    # import re
    # # ws = df.worksheet('Sheet1')
    # for index, row in df.iterrows():
    #     for col in range(len(row)):
    #         # print("Checking cell: " + str(index) + " " + str(col))
    #         if str(df.iloc[index, col]).startswith("="):
    #             print("Found equal sign in cell: " + str(df.iloc[index, col]))
    #             df.at[index, col] = str(df.iloc[index, col]).replace("=", " =") 
    #             print("Replaced equal sign in cell: " + str(df.iloc[index, col]))

    # Save data to a file
    # print("Saving data to a file...")
    # df.to_excel(r'.\data.xlsx', index=False, sheet_name='raw_data')
    print("Done!")
    return df
