#this is a script to feed multiple FED device files for the maze dispenser code
#upload all FED files for each mouse, and it will create a masterfile with time elapsed, sort it into pellet retrieval time and pellet count columns for easy analysis and comparison
import pandas as pd
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timedelta

def seconds_to_hhmmss(seconds):
    return str(timedelta(seconds=int(seconds)))

def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select CSV Files",
        filetypes=[("CSV files", "*.csv")]
    )
    return list(file_paths)

def save_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.asksaveasfilename(
        title="Save Processed Data",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialdir=str(Path.home() / "Downloads")
    )
    return file_path if file_path else None

def process_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Assuming timestamp is in the first column
    timestamp_col = df.columns[0]
    
    # Convert timestamps to datetime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    # Calculate time elapsed in seconds from the first timestamp
    first_timestamp = df[timestamp_col].min()
    seconds_elapsed = (df[timestamp_col] - first_timestamp).dt.total_seconds()
    
    # Convert seconds to HH:MM:SS format
    df['time_elapsed'] = seconds_elapsed.apply(seconds_to_hhmmss)
    
    # Extract pellet_count (column R) and retrieval_time (column T)
    # Convert column indices: R is 17th column (0-based index 16), T is 19th column (0-based index 18)
    source_name = Path(file_path).stem
    df[f'{source_name}_pellet_count'] = df.iloc[:, 17]  # Column R
    df[f'{source_name}_retrieval_time'] = df.iloc[:, 19]  # Column T
    
    # Keep only the new columns
    df = df[['time_elapsed', f'{source_name}_pellet_count', f'{source_name}_retrieval_time']]
    
    return df

def merge_dataframes(dfs):
    # Create a list to store all unique time_elapsed values
    all_times = []
    for df in dfs:
        all_times.extend(df['time_elapsed'].tolist())
    
    # Remove duplicates and sort
    unique_times = sorted(list(set(all_times)))
    
    # Create a new dataframe with the time_elapsed column
    merged_df = pd.DataFrame({'time_elapsed': unique_times})
    
    # For each source dataframe, merge its data
    for df in dfs:
        # Get the source-specific column names (they'll be like 'sourcename_pellet_count')
        source_cols = [col for col in df.columns if col != 'time_elapsed']
        
        # Merge with the main dataframe
        merged_df = merged_df.merge(df[['time_elapsed'] + source_cols], 
                                  on='time_elapsed', 
                                  how='left')
    
    # Add comparison columns
    # First, create a combined pellet count column
    pellet_cols = [col for col in merged_df.columns if col.endswith('_pellet_count')]
    merged_df['comparison_pellet_count'] = merged_df[pellet_cols].mean(axis=1)
    
    # Then create separate retrieval time columns for comparison
    retrieval_cols = [col for col in merged_df.columns if col.endswith('_retrieval_time')]
    for col in retrieval_cols:
        source_name = col.replace('_retrieval_time', '')
        merged_df[f'comparison_{source_name}_retrieval'] = merged_df[col]
    
    return merged_df

def main():
    while True:
        # Select CSV files
        print("\n--- New Batch Processing ---")
        file_paths = select_files()
        if not file_paths:
            print("No files selected. Please select files for processing.")
            continue
        
        # Process each file and store in a list
        processed_dfs = []
        for file_path in file_paths:
            try:
                df = process_csv(file_path)
                processed_dfs.append(df)
                print(f"Successfully processed {Path(file_path).name}")
            except Exception as e:
                print(f"Error processing {Path(file_path).name}: {str(e)}")
        
        if not processed_dfs:
            print("No files were successfully processed. Please try again.")
            continue
        
        # Merge all dataframes with the new format
        combined_df = merge_dataframes(processed_dfs)
        
        # Let user choose where to save the file
        output_path = save_file()
        if output_path:
            combined_df.to_csv(output_path, index=False)
            print(f"\nProcessed data saved to: {output_path}")
            print("\nReady for next batch of files...")
        else:
            print("\nSave cancelled. Ready for next batch of files...")

if __name__ == "__main__":
    main()
