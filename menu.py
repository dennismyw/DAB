# GUI menu 
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import json
from tkinter import simpledialog
import matplotlib.pyplot as plt
import seaborn as sns
import pymongo
from datetime import datetime
from data_cleaning import clean_data
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

class DataManipulationGUI:
    def __init__(self, root):
         # Connect to MongoDB
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['summative']
        self.antenna_data = None
        self.params_data = None
        self.new_columns_data = pd.DataFrame() 
        self.root = root
        self.root.title("Data Manipulation GUI")
        self.filtered_data = None
        # Create widgets
        self.btn_load_antenna_data = tk.Button(root, text="Load Antenna Data", command=self.load_antenna_data)
        self.btn_load_params_data = tk.Button(root, text="Load params Data", command=self.load_params_data)
        self.btn_save_prepared_data = tk.Button(root, text="Save Prepared Data", command=self.save_prepared_data)
        self.btn_clean_data = tk.Button(root, text="Clean Data", command=self.clean_data)
        self.btn_generate_json = tk.Button(root, text="Save file as JSON", command=self.generate_json)
        self.lbl_ant_loaded = tk.Label(root, text="Antenna file not yet loaded")
        self.lbl_remarks = tk.Label(root, text="Clean data before process data")
        self.lbl_para_loaded = tk.Label(root, text="Params file not yet loaded")
        self.load_button = tk.Button(self.root, text="Load Data", command=self.load_data)
        
        #console widget
        self.log_console_label = tk.Label(root, text="Log")
        self.result_console_label = tk.Label(root, text="Output Result")            
        self.log_console = tk.Text(root, height=10, width=70, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)     
        self.result_console = tk.Text(root, height=10, width=70, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        log_scrollbar = tk.Scrollbar(root, command=self.log_console.yview)
        result_scrollbar = tk.Scrollbar(root, command=self.result_console.yview)
        self.result_console.config(yscrollcommand=result_scrollbar.set)
        self.btn_confirm_action = tk.Button(root, text="Confirm Action", command=self.confirm_action)
        self.result_scrollbar_y = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.result_console.yview)
        self.result_scrollbar_x = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.result_console.xview)
        self.result_console.config(yscrollcommand=self.result_scrollbar_y.set, xscrollcommand=self.result_scrollbar_x.set)
        # Grid layout
        self.options_list = [
            "1. Exclude the 'NGR' : NZ02553847, SE213515, NT05399374 and NT252675908",
            "2. Extraction 'EID' of  C18A, C18F, C188",
            "3. Produce the mean, mode and median for the 'In-Use ERP Total'",
            "4. A bar chart displays the selected information",
            "5. Determine if there is any significant correlation"
        ]
        self.selected_option = tk.StringVar(root)
        self.selected_option.set(self.options_list[0])  # Set the default option
        self.option_menu = tk.OptionMenu(root, self.selected_option, *self.options_list, command=self.handle_option_selection)
        self.handle_option_selection(self.options_list[0])
        
        self.btn_load_antenna_data.grid (row=0, column=0, padx=10, pady=10, sticky="ew")
        self.btn_load_params_data.grid  (row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.btn_save_prepared_data.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.load_button.grid           (row=0, column=3, padx=10, pady=10, sticky="ew")
        self.btn_generate_json.grid     (row=0, column=4, padx=10, pady=10, sticky="ew")
 
        self.lbl_ant_loaded.grid        (row=1, column=0, columnspan=1, padx=10, pady=5, sticky="w")
        self.lbl_para_loaded.grid       (row=1, column=1, columnspan=1, padx=10, pady=5, sticky="w")    
        self.btn_clean_data.grid        (row=1, column=2, padx=10, pady=10, sticky="ew")
        self.lbl_remarks.grid           (row=1, column=3, columnspan=1, padx=10, pady=5, sticky="w")
        self.option_menu.grid           (row=2, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        self.btn_confirm_action.grid    (row=3, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        self.log_console_label.grid     (row=4, column=0, padx=5, pady=5, sticky="w")
        self.log_console.grid           (row=5, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        log_scrollbar.grid              (row=5, column=4, sticky='ns', pady=5)
        self.result_console_label.grid  (row=6, column=0, padx=10, pady=5, sticky="w")
        self.result_console.grid        (row=7, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        result_scrollbar.grid           (row=7, column=4, sticky='ns', pady=5)
        self.result_scrollbar_x.grid    (row=8, column=0, columnspan=4, sticky='ew', padx=10, pady=5)

        root.grid_rowconfigure(3, weight=1)
        root.grid_rowconfigure(5, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)
        root.grid_columnconfigure(4, weight=1) 

    def display_log(self, data):
        current_content = self.log_console.get("1.0", tk.END)
        new_content = f"{data}\n{'-'*20}\n{current_content}"
        
        self.log_console.delete("1.0", tk.END)
        self.log_console.insert("1.0", new_content)
        self.log_console.see("1.0")  # Scroll to the top of the text widget

    def display_result_console(self,data):
        self.result_console.delete("1.0", tk.END)
        self.result_console.see(tk.END)
        self.result_console.insert(tk.END, data)
        
    def handle_option_selection(self, option):
        self.selected_option = option

    def confirm_action(self):
        if self.selected_option == self.options_list[0]:
            self.option_1()
        elif self.selected_option == self.options_list[1]:
            self.option_2()
        elif self.selected_option == self.options_list[2]:
            self.option_3()
        elif self.selected_option == self.options_list[3]:
            self.option_4()
        elif self.selected_option == self.options_list[4]:
            self.option_5()

    def load_antenna_data(self):
        file_path = filedialog.askopenfilename(title="Select Antenna Data File", filetypes=[("CSV Files", "*.csv")])
      
        if not file_path:
            # If the user cancels the file dialog, do nothing
            return     
        try:
            # Check if 'NGR' column exists in the DataFrame
            self.antenna_data = pd.read_csv(file_path, encoding="ISO-8859-1")
            if 'NGR' not in self.antenna_data.columns:
                self.display_log("Error: The 'NGR' column is missing in the CSV data. Please load a correct antenna.csv file.")
                self.antenna_data = None  # Set self.antenna_data to None to indicate that it's invalid
            else:
                self.display_log("An Antenna file loaded")
                self.lbl_ant_loaded.config(text="Antenna file loaded")
           
        except Exception as e:
            # If an error occurs during reading or displaying the data, show an error message
            self.display_log(f"Error: {str(e)}\n")

    def load_params_data(self):
        file_path = filedialog.askopenfilename(title="Select Params Data File", filetypes=[("CSV Files", "*.csv")])
        
        if not file_path:
            # If the user cancels the file dialog, do nothing
            return
        self.params_data = pd.read_csv(file_path, encoding="ISO-8859-1")
        try:
            if 'EID' not in self.params_data.columns:
                self.display_log("Error: The 'EID' column is missing in the CSV data. Please load a correct params.csv file.")
                self.params_data = None 
            else:
                self.display_log( "An Params file loaded")
                self.lbl_para_loaded.config(text="Params file loaded")
        except Exception as e:
           self.display_log(f"Error: {str(e)}\n")

    def save_prepared_data(self):
        try:
            if self.filtered_data is not None:
                self.save_to_mongodb(self.filtered_data, 'filtered_data_collection')
                self.display_log("Filtered data saved to MongoDB.")
            
            if self.merged_data is not None:
                self.save_to_mongodb(self.merged_data, 'merged_data_collection')
                self.display_log("Merged data saved to MongoDB.")
            
            if self.calculated_result is not None:
                self.save_to_mongodb(self.calculated_result, 'calculated_result_collection')
                self.display_log("Calculated result saved to MongoDB.")
            
            if self.filtered_data is None and self.merged_data is None and self.calculated_result is None:
                self.display_log("No data to save.")
                
        except Exception as e:
            self.display_log("An error occurred: " + str(e))

    def save_to_mongodb(self, data, collection_name):
        collection = self.db[collection_name]
        records = data.to_dict('records')
        collection.insert_many(records)   

    def retrieve_data(self, collection_name):
        collection = self.db[collection_name]
        # Exclude the _id field from the retrieved data
        data = collection.find({}, {'_id': 0})
        data_df = pd.DataFrame(data)
        return data_df

    def load_data(self):
        try:
            self.filtered_data = self.retrieve_data('filtered_data_collection')
            self.merged_data = self.retrieve_data('merged_data_collection')
            self.calculated_result = self.retrieve_data('calculated_result_collection')
            self.display_log("Data retrieved")
            # Display the data in the result console
            result_text = f"Filtered Data:\n{self.filtered_data.head}\n\n" \
                            f"Merged Data:\n{self.merged_data.head}\n\n" \
                            f"Calculated Result:\n{self.calculated_result.head}"

            self.display_result_console(result_text)

        except Exception as e:
            error_text = f"An error occurred: {e}"
            self.result_console.delete(1.0, tk.END)  # Clear the result console
            self.result_console.insert(tk.END, error_text)
    
    def clean_data(self):
        if self.params_data is not None and self.antenna_data is not None:
            # Call the clean_data function from the imported module
            self.params_data, self.antenna_data = clean_data(self.params_data, self.antenna_data, self.display_log)
      
    def generate_json(self):
        if self.antenna_data is None:
            self.lbl_ant_loaded.config(text="Antenna file not yet loaded")
        else:
            self.lbl_ant_loaded.config(text="Antenna file loaded")
        json_name = simpledialog.askstring("Input", "Enter the file name of json for Antenna file:")
        if json_name is None:
            return
        try:
            antenna_dict = self.antenna_data.to_dict(orient="records")
            with open(json_name + '.json', 'w') as json_file:
                json.dump(antenna_dict, json_file)
            self.display_log(f"JSON file '{json_name}.json' saved successfully.")
        except Exception as e:
            self.display_log(f"Failed to save JSON file: {e}")   
        
        if self.params_data is None:
            self.lbl_ant_loaded.config(text="Params file not yet loaded")
        else:
            self.lbl_ant_loaded.config(text="Params file loaded")
        json_name = simpledialog.askstring("Input", "Enter the file name of json for Params file:")
        if json_name is None:
            return
        try:
            self.params_data['Date'] = self.params_data['Date'].astype(str)
            params_dict = self.params_data.to_dict(orient="records")
            with open(json_name + '.json', 'w') as json_file:
                json.dump(params_dict, json_file)
            self.display_log(f"JSON file '{json_name}.json' saved successfully.")
        except Exception as e:
            self.display_log(f"Failed to save JSON file: {e}")   

    def option_1(self):
        try:
            # self.filtered_data = None
            excluded_ngrs = ['NZ02553847', 'SE213515', 'NT05399374', 'NT25265908']
            self.filtered_data = self.antenna_data[~self.antenna_data['NGR'].isin(excluded_ngrs)]
            self.display_log("NGRs: NZ02553847, SE213515, NT05399374, and NT25265908 have been excluded.\n")
            # Display a summary or subset of the filtered_data instead of the entire DataFrame
            self.display_result_console(self.filtered_data.head())
        except Exception as e:
            self.display_log("An error occurred:"+ str(e))

    def option_2(self):
        try:
            if self.filtered_data is None:
                self.display_log("Error: 'new_columns_data' is not set. Please load data first.")
                return
            
            target_eids = ['C18A', 'C18F', 'C188']
            self.new_columns_data = self.params_data[self.params_data['EID'].isin(target_eids)]
            
            # Check if 'id' column exists in both DataFrames
            if 'id' not in self.new_columns_data.columns or 'id' not in self.filtered_data.columns:
                self.display_log("Error: 'id' column not found in both DataFrames.")
                return

            # Check if data types are the same for the 'id' column in both DataFrames
            if self.new_columns_data['id'].dtype != self.filtered_data['id'].dtype:
                self.display_log("Error: Data type of 'id' column is not the same in both DataFrames.")
                return

            # Select the columns to merge from filtered_data
            merge_columns = ['id', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']
            self.merged_data = pd.merge(
                self.new_columns_data,
                self.filtered_data[merge_columns],
                on='id',
                suffixes=('', '_merged')
            )
            self.merged_data.rename(columns={'In-Use Ae Ht': 'Aerial height(m)', 'In-Use ERP Total': 'Power(kW)'}, inplace=True)
            self.display_result_console(self.merged_data)
            self.display_log("EID have been extracted")
        except Exception as e:
            self.display_log("An error occurred:"+ str(e))

    def option_3(self):
        try:
            if self.merged_data is None:
                self.display_log("Error: 'merged_data' is not set. Please perform the merge operation first.")
                return

            # Filtering based on Site Height
            height_data = self.merged_data[self.merged_data['Site Height'] > 75].copy()

            # Filtering based on Date from 2001 onwards
            start_date = datetime(2001, 1, 1)
            height_data_bydate = self.merged_data[self.merged_data['Date'] >= start_date].copy()

            # Calculate mean, mode, and median for 'Power(kW)' in the filtered data
            mean_erp_total_height = height_data['Power(kW)'].mean()
            mode_erp_total_height = height_data['Power(kW)'].mode().values[0]
            median_erp_total_height = height_data['Power(kW)'].median()

            # Calculate mean, mode, and median for 'Power(kW)' in the filtered data by date
            mean_erp_total_bydate = height_data_bydate['Power(kW)'].mean()
            mode_erp_total_bydate = height_data_bydate['Power(kW)'].mode().values[0]
            median_erp_total_bydate = height_data_bydate['Power(kW)'].median()

            # Create DataFrames for the results
            result_data = {
                "Metric": ["Mean", "Mode", "Median"],
                "Site Height > 75": [mean_erp_total_height, mode_erp_total_height, median_erp_total_height],
                "Date from 2001 onwards": [mean_erp_total_bydate, mode_erp_total_bydate, median_erp_total_bydate]
            }
            self.calculated_result = pd.DataFrame(result_data)

            # Display the DataFrame
            self.display_result_console(self.calculated_result)
        except Exception as e:
            self.display_log("An error occurred:"+ str(e))
  
    def option_4(self):
        try:
            selected_columns = ['EID', 'Site','Freq.', 'Block', 'Serv Label1','Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']
            df = self.merged_data.loc[:, selected_columns]
                
            # Define the columns you want to count
            count_columns = ["Freq.", "Block", "Serv Label1", "Serv Label2", 'Serv Label3', 'Serv Label4', 'Serv Label10']

            # Group by EID and aggregate counts for each column
            agg_dict = {column: "count" for column in count_columns}
            grouped_counts = df.groupby("EID").agg(agg_dict)
            # Reset index and melt the DataFrame for Seaborn
            melted_data = grouped_counts.reset_index().melt(id_vars=['EID'], value_vars=count_columns, var_name='Column', value_name='Count')
            # Use Seaborn to create the grouped bar chart
            sns.set(style="whitegrid")  # Set the style
            plt.figure(figsize=(10, 6))
            ax = sns.barplot(data=melted_data, x='EID', y='Count', hue='Column')

            plt.title("Counts of Items by EID")
            plt.xlabel("EID")
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            sns.despine()  # Remove spines
            plt.show()

        except Exception as e:
            self.display_log("An error occurred:"+ str(e))

    def option_5(self):
        try:
            selected_columns = ['Freq.', 'Block', 'Serv Label1','Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']
            df = self.merged_data.loc[:, selected_columns]
            # Convert categorical columns to numeric representations using label encoding
            categorical_columns = ['Freq.','Block', 'Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']
            for column in categorical_columns:
                df[column] = df[column].astype("category").cat.codes             
            # Calculate correlation matrix
            correlation_matrix = df[categorical_columns].corr()
            # Create a heatmap
            plt.figure(figsize=(12, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", center=0)
            plt.title("Correlation Heatmap")
            plt.show()
        except Exception as e:
            self.display_log("An error occurred:"+ str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DataManipulationGUI(root)
    root.mainloop()
