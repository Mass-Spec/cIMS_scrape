import pandas as pd 
import numpy as np
import os
import os.path
import dtale
import subprocess
import webbrowser
import shutil

# Define the CSV file to read

file =  "C:\\Users\\Administrator\\Desktop\\CSV_Experiments\\cIMS_CSV.csv"

if os.path.exists(file):
	master_df = pd.read_csv(file, engine = 'python')
else:
	master_df = ()


# Format dataframe as table for display using dtale

if __name__ == '__main__':
   
    dtale.show(pd.DataFrame(master_df), host='localhost', subprocess=False, open_browser = True)


