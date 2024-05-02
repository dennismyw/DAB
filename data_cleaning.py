import pandas as pd

def clean_data(params_data, antenna_data,display_log):
    # Remove the extra space at the end of the index labels
    params_data.columns = params_data.columns.str.rstrip()
    # fill the missing date and standized the format
    params_data['Date'].fillna(pd.to_datetime('today'), inplace=True)
        # Convert 'Date' column to datetime format
    params_data['Date'] = pd.to_datetime(params_data['Date'], format='%d/%m/%Y', errors='coerce')
    display_log("The missing Date have been filled.")

    # Fill missing values in the 'TII Main Id (Hex)' column with 'Unknown'
    params_data['TII Main Id (Hex)'].replace("", pd.NA, inplace=True)
    params_data['TII Sub Id (Hex)'].replace("", pd.NA, inplace=True)
    display_log("The missing TII Main Id (Hex) have been filled.")

    label_columns = ['Serv Label1', 'SId 1 (Hex)', 'LSN 1 (Hex)','Serv Label2', 'SId 2 (Hex)', 'LSN 2 (Hex)',  ]

    # Group the data by EID and forward-fill missing values within each group
    params_data[label_columns] = params_data.groupby('EID')[label_columns].ffill()
    params_data.loc[:, label_columns] = params_data.loc[:, label_columns].replace("", pd.NA)

    params_data.reset_index(drop=True, inplace=True)
    display_log("The missing Serv Label have been filled.")

    numeric_columns = ['In-Use ERP Total', 'Dir Max ERP', '0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100',
            '110', '120', '130', '140', '150', '160', '170', '180', '190', '200',
            '210', '220', '230', '240', '250', '260', '270', '280', '290', '300',
            '310', '320', '330', '340']
    antenna_data[numeric_columns] = antenna_data[numeric_columns].replace(',', '', regex=True).astype(float)

    # Fill missing values in each numeric column with the mean of that column
    for label in numeric_columns:
        antenna_data.loc[:, label].fillna(antenna_data[label].mean(), inplace=True)
    display_log("The numeric columns have been filled with mean.")
    
    return params_data, antenna_data