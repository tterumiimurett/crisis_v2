import pandas as pd
import os
import json
from collections import defaultdict

# Configurations
DATA_DIR = 'data'
OUTPUT_DIR = 'output'

def process_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    merged_data = defaultdict(list)
    
    # Process all Excel files in DATA_DIR
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith('.xlsx'):
            continue
            
        file_path = os.path.join(DATA_DIR, filename)
        print(f"Processing {filename}...")
        
        try:
            # Read Excel file
            # Note: For choices数据.xlsx, the ID column header is missing, pandas calls it 'Unnamed: 1'
            df = pd.read_excel(file_path)
            
            # Normalize ID column names
            # Map known ID column variations to 'id'
            column_mapping = {
                'Unnamed: 1': 'id',
                'l录音': 'id',
                '录音': 'id'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # Check if 'id' column exists
            if 'id' not in df.columns:
                print(f"Warning: No 'id' column found in {filename}. Columns found: {list(df.columns)}")
                continue
                
            # Convert ID to string to ensure consistency (remove .0 for floats)
            df['id'] = df['id'].astype(str).str.replace(r'\.0$', '', regex=True)
            
            # Convert to list of dictionaries
            records = df.to_dict(orient='records')
            
            # Save individual JSON file
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(OUTPUT_DIR, json_filename)
            
            # Custom encoder for JSON to handle NaN/floats etc if needed, 
            # but pandas to_dict usually handles basic types. 
            # We use json.dump default which might fail on timestamps/NaNs.
            # Pandas 'records' converts NaNs to nan (float). JSON standard doesn't support NaN.
            # Let's clean records: replace float('nan') with None
            
            cleaned_records = []
            for record in records:
                clean_rec = {}
                for k, v in record.items():
                    if pd.isna(v):
                        clean_rec[k] = None
                    else:
                        clean_rec[k] = v
                cleaned_records.append(clean_rec)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_records, f, ensure_ascii=False, indent=4)
            print(f"Saved {json_filename}")
            
            # Add to merged data
            for record in cleaned_records:
                rec_id = record.get('id')
                if rec_id:
                    # Add source file info if useful, strictly not requested but good for debugging
                    record['_source_file'] = filename 
                    merged_data[rec_id].append(record)
                    
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Save merged data
    merged_output_path = os.path.join(OUTPUT_DIR, 'merged_by_id.json')
    with open(merged_output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
    print(f"Saved merged data to {merged_output_path}")

if __name__ == '__main__':
    process_data()
