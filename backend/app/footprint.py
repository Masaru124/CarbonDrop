import pandas as pd
from rapidfuzz import process, fuzz
import os

class FootprintMatcher:
    def __init__(self, dataset_df):
        self.df = dataset_df.copy()
        self.choices = list(self.df['item'])

    def match_and_compute(self, items):
        results = []
        total = 0.0
        for it in items:
            name = it.get('name', '').strip()
            qty = float(it.get('qty', 1) or 1)
            best = process.extractOne(name, self.choices, scorer=fuzz.WRatio, score_cutoff=60)
            if best:
                matched_name, score, idx = best
                row = self.df[self.df['item'] == matched_name].iloc[0]
                co2_per_unit = float(row['co2'])
                unit = row['unit']
                footprint = round(qty * co2_per_unit, 4)
                results.append({'name': name, 'matched_name': matched_name, 'match_score': int(score),
                                'qty': qty, 'unit': unit, 'co2_per_unit': co2_per_unit,
                                'footprint': footprint})
                total += footprint
            else:
                results.append({'name': name, 'matched_name': None, 'match_score': 0,
                                'qty': qty, 'unit': None, 'co2_per_unit': None,
                                'footprint': 0.0})
        return results, round(total, 4)

def load_dataset(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'Dataset not found: {csv_path}')
    
    # Load the dataset
    df = pd.read_csv(csv_path)
    
    # Check if this is the greenhouse gas emissions dataset by looking at column names
    if 'Entity' in df.columns and 'GHG emissions per kilogram (Poore & Nemecek, 2018)' in df.columns:
        # Transform the greenhouse gas emissions dataset to match expected structure
        df = df.rename(columns={
            'Entity': 'item',
            'GHG emissions per kilogram (Poore & Nemecek, 2018)': 'co2'
        })
        # Add unit column (all items are per kilogram in this dataset)
        df['unit'] = 'kg'
        # Drop the Year column as it's not needed
        df = df.drop(columns=['Year'])
    else:
        # Handle the original footprint dataset structure
        df['item'] = df['item'].astype(str).str.strip()
    
    # Ensure item names are stripped of whitespace
    df['item'] = df['item'].astype(str).str.strip()
    return df
