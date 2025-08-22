import pandas as pd
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime, timedelta
import os

def seconds_to_hhmmss(seconds):
    return str(timedelta(seconds=int(seconds)))

class FedProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FED File Processor")
        self.root.geometry("800x600")
        
        # Set TK_SILENCE_DEPRECATION to suppress macOS Tk deprecation warning
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        
        # Use system default theme - most reliable across platforms
        self.processed_dfs = []
        self.selected_files = []
        
        # Create frames with explicit background colors
        self.create_title_frame()
        self.create_file_selection_frame()
        self.create_file_list_frame()
        self.create_status_frame()
        self.create_action_buttons_frame()
    
    def create_title_frame(self):
        frame = tk.Frame(self.root, bg="#e1e1e1", pady=10)
        frame.pack(fill=tk.X)
        
        title = tk.Label(frame, text="FED File Processor", 
                        font=("Helvetica", 16, "bold"),
                        bg="#e1e1e1")
        title.pack()
    
    def create_file_selection_frame(self):
        frame = tk.LabelFrame(self.root, text="File Selection", 
                             padx=10, pady=10, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        select_btn = tk.Button(frame, text="Select CSV Files", 
                              command=self.select_files,
                              bg="#dcdcdc", padx=10)
        select_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(frame, text="Clear Selection", 
                             command=self.clear_selection,
                             bg="#dcdcdc", padx=10)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_count_label = tk.Label(frame, text="No files selected", bg="#f0f0f0")
        self.file_count_label.pack(side=tk.LEFT, padx=20)
    
    def create_file_list_frame(self):
        frame = tk.LabelFrame(self.root, text="Selected Files", 
                             padx=10, pady=10, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a scrollable listbox
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set,
                                      bg="white", bd=1)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.file_listbox.yview)
    
    def create_status_frame(self):
        frame = tk.LabelFrame(self.root, text="Status", 
                             padx=10, pady=10, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(frame, text="Ready to process files", bg="#f0f0f0")
        self.status_label.pack(fill=tk.X)
        
        # Add progress bar
        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, 
                                       length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
    
    def create_action_buttons_frame(self):
        frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        process_btn = tk.Button(frame, text="Process Files", 
                               command=self.process_files,
                               bg="#dcdcdc", padx=10)
        process_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(frame, text="Save Results", 
                            command=self.save_results,
                            bg="#dcdcdc", padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(frame, text="Reset", 
                             command=self.reset_app,
                             bg="#dcdcdc", padx=10)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(frame, text="Exit", 
                            command=self.root.destroy,
                            bg="#dcdcdc", padx=10)
        exit_btn.pack(side=tk.RIGHT, padx=5)
    
    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_paths:
            self.selected_files = list(file_paths)
            self.update_file_list()
            self.file_count_label.config(text=f"{len(self.selected_files)} files selected")
            self.status_label.config(text="Files selected. Ready to process.")
    
    def clear_selection(self):
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="No files selected")
        self.status_label.config(text="Selection cleared")
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            self.file_listbox.insert(tk.END, Path(file_path).name)
    
    def process_files(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files to process first.")
            return
        
        self.processed_dfs = []
        self.progress['value'] = 0
        total_files = len(self.selected_files)
        
        for i, file_path in enumerate(self.selected_files):
            try:
                self.status_label.config(text=f"Processing {Path(file_path).name}...")
                self.root.update()
                
                df = self.process_csv(file_path)
                self.processed_dfs.append(df)
                
                # Update progress
                self.progress['value'] = (i + 1) / total_files * 100
                self.root.update()
                
            except Exception as e:
                messagebox.showerror("Processing Error", f"Error processing {Path(file_path).name}: {str(e)}")
        
        if self.processed_dfs:
            self.status_label.config(text=f"Successfully processed {len(self.processed_dfs)} files. Ready to save.")
        else:
            self.status_label.config(text="No files were successfully processed.")
    
    def process_csv(self, file_path):
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
    
    def merge_dataframes(self, dfs):
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
    
    def save_results(self):
        if not self.processed_dfs:
            messagebox.showwarning("No Data", "No processed data to save. Please process files first.")
            return
        
        # Merge all dataframes
        self.status_label.config(text="Merging data...")
        self.root.update()
        
        combined_df = self.merge_dataframes(self.processed_dfs)
        
        # Let user choose where to save the file
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialdir=str(Path.home() / "Downloads")
        )
        
        if file_path:
            combined_df.to_csv(file_path, index=False)
            self.status_label.config(text=f"Data saved to: {Path(file_path).name}")
            messagebox.showinfo("Success", f"Data successfully saved to:\n{file_path}")
        else:
            self.status_label.config(text="Save cancelled")
    
    def reset_app(self):
        self.selected_files = []
        self.processed_dfs = []
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="No files selected")
        self.status_label.config(text="Ready to process files")
        self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = FedProcessorApp(root)
    root.mainloop()
