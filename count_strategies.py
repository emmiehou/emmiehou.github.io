import pandas as pd
from google.colab import files
import io
from datetime import datetime, timedelta

def count_strategies(df):
    try:
        print("\nStarting data processing...")
        print(f"Initial columns: {df.columns.tolist()}")
        
        # Convert the first column to datetime
        time_col = df.columns[0]
        print(f"\nConverting time column: {time_col}")
        try:
            df[time_col] = pd.to_datetime(df[time_col])
        except Exception as e:
            print(f"Error converting time column: {str(e)}")
            print(f"First few values of time column:\n{df[time_col].head()}")
            raise
        
        # Get the timestamp of the first event
        first_event_time = df[time_col].min()
        print(f"\nFirst event time: {first_event_time}")
        
        # Calculate the cutoff time (1 hour after first event)
        cutoff_time = first_event_time + timedelta(hours=1)
        print(f"Cutoff time: {cutoff_time}")
        
        # Filter dataframe to only include events within the first hour
        df = df[df[time_col] <= cutoff_time]
        print(f"Events within first hour: {len(df)}")
        
        print("\nLocating required columns...")
        # Try to find the right columns, supporting both numeric and letter-based indices
        events_col = None
        if 'H' in df.columns:
            events_col = 'H'
            print("Found events column 'H'")
        elif 7 in df.columns:  # 0-based index for column H
            events_col = 7
            print("Found events column at index 7")
        else:
            # Try to find the events column by position
            try:
                events_col = df.columns[7]  # 0-based index for column H
                print(f"Using column at position 7: {events_col}")
            except IndexError:
                print("\nERROR: Could not find events column. Available columns:")
                for i, col in enumerate(df.columns):
                    print(f"Column {i}: {col}")
                raise ValueError("Events column not found at position 7")
        
        # Get other columns by position
        rule_shift_col = df.columns[14]  # Column 15 (0-based index 14)
        active_poke_col = df.columns[7]  # Column 8 (0-based index 7) - Events column
        correct_poke_col = df.columns[8]  # Column 9 (0-based index 8) - Active Poke column
        trial_col = df.columns[12]  # Column 13 (0-based index 12)
        
        # Create a copy of the DataFrame to avoid SettingWithCopyWarning
        df = df.copy()
        
        # Convert all relevant columns to lowercase for case-insensitive matching
        df[events_col] = df[events_col].astype(str).str.lower()
        df[active_poke_col] = df[active_poke_col].astype(str).str.lower()
        df[correct_poke_col] = df[correct_poke_col].astype(str).str.lower()
        
        # Define all event types to track in specific order
        event_types = [
            'losestay', 'loseshift', 'winshift', 'winstay', 
            'left', 'right', 'pellet', 'leftwithpellet', 
            'rightwithpellet', 'leftduringdispense', 'rightduringdispense',
            'correct', 'incorrect'  # Add new types for tracking correct/incorrect choices
        ]
        
        # Filter for rows where active_poke is 'left' or 'right' and create a new DataFrame
        df = df[df[correct_poke_col].isin(['left', 'right'])]
        
        # Get total counts using exact matching
        total_counts = {}
        for event in event_types[:-2]:  # Exclude correct/incorrect
            total_counts[event] = df[df[events_col].str.lower() == event.lower()].shape[0]
        
        # Convert total counts to DataFrame with specific order
        total_counts_df = pd.DataFrame([(event, total_counts[event]) for event in event_types[:-2]],
                                     columns=['TOTAL', 'FREQUENCY'])
        total_counts_df.set_index('TOTAL', inplace=True)
        
        # Sort DataFrame by trial number to ensure chronological order
        df = df.sort_values(by=trial_col)
        
        # Get unique phases and sort them in correct order (IA, 1, 2, 3, etc.)
        def phase_sort_key(x):
            if x == 'IA':
                return -1
            try:
                return int(x)  # Convert phase number to integer for proper sorting
            except ValueError:
                return float('inf')  # Put any non-numeric phases at the end
        
        unique_phases = sorted(df[rule_shift_col].unique(), key=phase_sort_key)
        print(f"\nFound rule shift phases in order: {unique_phases}")
        
        # Create a DataFrame for phase-specific counts
        phase_data = []
        phase_correct_choices = {}  # Store the correct choice for each phase
        trials_to_shift = {}  # For tracking trials between phases
        
        # First pass: get correct choices for each phase
        for phase in unique_phases:
            phase_df = df[df[rule_shift_col] == phase]
            if not phase_df.empty:
                correct_choice = phase_df[correct_poke_col].iloc[0].lower()
                phase_correct_choices[phase] = correct_choice
        
        # Second pass: count events for each phase
        for i, phase in enumerate(unique_phases):
            phase_df = df[df[rule_shift_col] == phase]
            if phase_df.empty:
                continue
                
            correct_choice = phase_correct_choices[phase]
            
            # Get counts for this phase using exact matching
            counts = {}
            for event in event_types[:-2]:  # Exclude correct/incorrect
                counts[event] = phase_df[phase_df[events_col].str.lower() == event.lower()].shape[0]
            
            # Count correct and incorrect choices for this phase only
            # Correct: when the event matches the correct choice
            # Incorrect: when the event is the opposite choice (if correct is 'left', only count 'right' as incorrect)
            opposite_choice = 'right' if correct_choice == 'left' else 'left'
            
            # Use phase_df to only count events in the current phase
            correct_count = phase_df[phase_df[events_col].str.lower() == correct_choice].shape[0]
            incorrect_count = phase_df[phase_df[events_col].str.lower() == opposite_choice].shape[0]
            
            counts['correct'] = correct_count
            counts['incorrect'] = incorrect_count
            
            # Add to phase data
            for event in event_types:  # Include correct/incorrect
                phase_data.append({
                    'Phase': phase,
                    'Event': event,
                    'Count': counts[event]
                })
            
            # Calculate trials to shift
            if i > 0:  # Skip first phase (IA) as it's the starting point
                phase_start_trial = phase_df[trial_col].iloc[0]  # First trial of current phase
                prev_phase_start = df[df[rule_shift_col] == unique_phases[i-1]][trial_col].iloc[0]  # First trial of previous phase
                trials_to_shift[unique_phases[i-1]] = phase_start_trial - prev_phase_start
        
        # Convert phase counts to DataFrame
        phase_counts_df = pd.DataFrame(phase_data)
        
        # Pivot the phase counts to create a nice table with specific event order
        # Ensure phases are in the correct order by specifying the columns parameter
        phase_counts_pivot = phase_counts_df.pivot(index='Event', 
                                                 columns='Phase', 
                                                 values='Count')
        
        # Reorder the columns to match the sorted unique_phases
        phase_counts_pivot = phase_counts_pivot[unique_phases]
        
        # Reorder the index to match event_types order
        phase_counts_pivot = phase_counts_pivot.reindex(event_types)
        
        # Add the trials to criterion row
        phase_counts_pivot.loc['trials to criterion'] = pd.Series(trials_to_shift)
        
        # Convert all values in the DataFrame to integers
        phase_counts_pivot = phase_counts_pivot.fillna(0).astype(int)
        
        # Rename columns to include correct choice
        phase_counts_pivot.columns = [f"{phase} [{phase_correct_choices[phase].upper()}]" for phase in unique_phases]
        
        # Calculate percentages for each phase and add as new rows
        for phase in unique_phases:
            strategy_counts = phase_counts_pivot.loc[['losestay', 'loseshift', 'winstay', 'winshift'], phase]
            # Calculate total only from the four strategies
            strategy_total = sum(phase_counts_pivot.loc[strategy, phase] for strategy in ['losestay', 'loseshift', 'winstay', 'winshift'])
            if strategy_total > 0:
                for strategy in ['losestay', 'loseshift', 'winstay', 'winshift']:
                    count = phase_counts_pivot.loc[strategy, phase]
                    percentage = (count / strategy_total) * 100
                    phase_counts_pivot.at[f'% {strategy}', phase] = f"{percentage:.1f}"
            else:
                for strategy in ['losestay', 'loseshift', 'winstay', 'winshift']:
                    phase_counts_pivot.at[f'% {strategy}', phase] = "0.0"
        
        return total_counts_df, phase_counts_pivot, None
        
    except Exception as e:
        print(f"\nError processing data: {str(e)}")
        return None, None, None

def main():
    while True:
        print("\nPlease upload your Excel (.xlsx, .xls) or CSV (.csv) file")
        print("(Upload a file with any other extension to exit)")
        uploaded = files.upload()
        
        if not uploaded:  # If no file was uploaded
            print("\nNo file uploaded. Exiting...")
            break
        
        for filename in uploaded.keys():
            # Convert filename to lowercase for case-insensitive comparison
            file_lower = filename.lower()
            try:
                if file_lower.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(uploaded[filename]))
                elif file_lower.endswith('.csv'):
                    # Try different encoding options if needed
                    try:
                        df = pd.read_csv(io.BytesIO(uploaded[filename]))
                    except UnicodeDecodeError:
                        df = pd.read_csv(io.BytesIO(uploaded[filename]), encoding='latin1')
                else:
                    print(f"\nUnsupported file format for {filename}. Exiting...")
                    return  # Exit the program
                    
                print(f"\nProcessing {filename}...")
                total_counts_df, phase_counts_pivot, _ = count_strategies(df)
                
                if total_counts_df is not None:
                    print(f"\nResults for {filename}:")
                    
                    print("\nTotal counts across all rule shift phases:")
                    display(total_counts_df.style
                           .set_properties(**{'text-align': 'left'})
                           .set_table_styles([
                               {'selector': 'th', 'props': [('text-align', 'left')]},
                               {'selector': '', 'props': [('border-collapse', 'collapse')]},
                               {'selector': 'td', 'props': [('padding-top', '0')]},
                               {'selector': 'th', 'props': [('padding-bottom', '0')]}
                           ]))
                    
                    print("\nCounts by rule shift phase:")
                    display(phase_counts_pivot.style
                           .set_properties(**{'text-align': 'left'})
                           .set_table_styles([
                               {'selector': 'th', 'props': [('text-align', 'left')]},
                               {'selector': '', 'props': [('border-collapse', 'collapse')]},
                               {'selector': 'td', 'props': [('padding-top', '0')]},
                               {'selector': 'th', 'props': [('padding-bottom', '0')]}
                           ]))
                else:
                    print(f"Error: Could not process {filename}. Please check if the file format and column structure are correct.")
                    
            except Exception as e:
                print(f"\nError processing {filename}: {str(e)}")
                print("Please make sure the file contains all required columns and data is in the correct format.")
        
        print("\n-----------------------------------")
        print("Ready for next file...")
        print("-----------------------------------")

if __name__ == "__main__":
    main()
