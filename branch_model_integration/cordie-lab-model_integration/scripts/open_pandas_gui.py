import pandas as pd
import pandasgui as pdg

# Read data from a file
print("Reading data from a file...")
df = pd.read_excel('data.xlsx')

# Show data in a GUI
print("Showing data in a GUI...")
pdg.show(df)

