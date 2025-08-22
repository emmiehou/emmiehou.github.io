#this is a script for extracting specific columns from a csv or excel file of Biobserve data

#!/usr/bin/env python3
"""
Extract Columns Script

This script allows users to upload a CSV or Excel file and extract specific columns.
It will extract columns with headers "visits" and "duration" as well as columns at specific positions.
"""

import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

class ColumnExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Column Extractor")
        self.root.geometry("600x400")
        
        # Create main frame with padding
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
        # Specific columns to extract (1-based index)
        self.specific_columns = [1, 2, 3, 4, 23, 26, 34, 37, 45, 48, 56, 59, 67, 70, 78, 81, 89, 92, 100, 103]
        # Convert to 0-based index for pandas
        self.specific_columns_0_based = [col-1 for col in self.specific_columns]
        
        # Headers to extract
        self.headers_to_extract = ["visits", "duration"]
        
    def create_widgets(self):
        # File selection section
        file_frame = tk.LabelFrame(self.main_frame, text="File Selection", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_path_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_button = tk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Status section
        status_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Ready to extract columns")
        status_label = tk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Action buttons
        button_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        extract_button = tk.Button(button_frame, text="Extract Columns", command=self.extract_columns)
        extract_button.pack(side=tk.RIGHT, padx=5)
        
        # Information section
        info_frame = tk.LabelFrame(self.main_frame, text="Information", padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_text = "This tool will extract:\n"
        info_text += "1. Columns with headers 'visits' and 'duration'\n"
        info_text += "2. Columns at positions: 1, 2, 3, 4, 23, 26, 34, 37, 45, 48, 56, 59, 67, 70, 78, 81, 89, 92, 100, 103\n"
        info_text += "3. Will delete the first 12 rows of the sheet\n\n"
        info_text += "Supported file formats: CSV and Excel (.xlsx, .xls)"
        
        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(fill=tk.BOTH, expand=True)
        
    def browse_file(self):
        filetypes = [
            ("Spreadsheet files", "*.csv *.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select a CSV or Excel file",
            filetypes=filetypes
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"Selected file: {Path(file_path).name}")
    
    def extract_columns(self):
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return
        
        try:
            # Update status
            self.status_var.set("Reading file...")
            self.root.update_idletasks()
            
            # Read the file based on extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format. Please use CSV or Excel files.")
                self.status_var.set("Error: Unsupported file format")
                return
                
            # Delete the first 12 rows as requested
            if len(df) > 12:
                df = df.iloc[12:].reset_index(drop=True)
                self.status_var.set("Removed first 12 rows...")
                self.root.update_idletasks()
            else:
                messagebox.showwarning("Warning", "The file has fewer than 12 rows. No rows were deleted.")
            
            # Extract columns by header
            header_columns = []
            for header in self.headers_to_extract:
                matching_cols = [col for col in df.columns if header.lower() in col.lower()]
                header_columns.extend(matching_cols)
            
            # Extract columns by position (ensure they exist)
            position_columns = []
            position_column_names = []
            for pos in self.specific_columns_0_based:
                if pos < len(df.columns):
                    position_columns.append(pos)
                    position_column_names.append(df.columns[pos])
            
            # Create a list to hold the final columns in the exact order we want
            all_columns = []
            
            # First, add columns by position in the exact order specified
            # This ensures the interval summary columns are at the far left
            for pos in self.specific_columns_0_based:
                if pos < len(df.columns):
                    col_name = df.columns[pos]
                    if col_name not in all_columns:  # Avoid duplicates
                        all_columns.append(col_name)
            
            # Then add any header-based columns that weren't already included
            for col in header_columns:
                if col not in all_columns:  # Avoid duplicates
                    all_columns.append(col)
            
            # Check if we found any columns
            if not all_columns:
                messagebox.showwarning("Warning", "No matching columns found in the file.")
                self.status_var.set("No matching columns found")
                return
            
            # Extract the columns while preserving order
            result_df = df[all_columns]
            
            # Save the result
            save_path = filedialog.asksaveasfilename(
                title="Save extracted columns",
                defaultextension=file_ext,
                filetypes=[
                    ("CSV file", "*.csv"),
                    ("Excel file", "*.xlsx")
                ],
                initialdir=str(Path(file_path).parent),
                initialfile=f"extracted_{Path(file_path).stem}{file_ext}"
            )
            
            if not save_path:
                self.status_var.set("Operation cancelled")
                return
            
            # Save based on extension
            save_ext = Path(save_path).suffix.lower()
            if save_ext == '.csv':
                result_df.to_csv(save_path, index=False)
            else:
                result_df.to_excel(save_path, index=False)
            
            self.status_var.set(f"Successfully extracted {len(all_columns)} columns to {Path(save_path).name}")
            messagebox.showinfo("Success", f"Successfully extracted {len(all_columns)} columns and removed first 12 rows. Saved to {Path(save_path).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = ColumnExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
