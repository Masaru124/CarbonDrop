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
    elif 'food_item' in df.columns and 'emissions_kg_co2_per_kg' in df.columns:
        # Handle combined_food_emissions.csv structure
        df = df.rename(columns={
            'food_item': 'item',
            'emissions_kg_co2_per_kg': 'co2'
        })
        df['unit'] = 'kg'
        # Clean 'item' column by trimming whitespace
        df['item'] = df['item'].astype(str).str.strip()
    else:
        # Handle the original footprint dataset structure
        df['item'] = df['item'].astype(str).str.strip()

    # Ensure item names are stripped of whitespace
    df['item'] = df['item'].astype(str).str.strip()
    return df

class WhatIfSimulator:
    def __init__(self, dataset_df):
        self.df = dataset_df.copy()
        # Define transport emission factors (kg CO2e per km)
        self.transport_factors = {
            'flight': 0.25,  # kg CO2e per km for short flights
            'train': 0.04    # kg CO2e per km for train
        }

    def simulate_meat_replacement(self, meat_meals_per_week, weeks=52):
        """
        Simulate replacing meat meals with plant-based alternatives.
        Assumes average meat meal is 200g beef, replaced with 200g lentils.
        """
        # Get CO2 for beef (meat)
        beef_row = self.df[self.df['item'].str.lower() == 'beef']
        if beef_row.empty:
            beef_co2 = 27.0  # Default value from dataset
        else:
            beef_co2 = float(beef_row['co2'].iloc[0])

        # Assume plant-based replacement (lentils or similar)
        plant_based_co2 = 0.9  # kg CO2e per kg for lentils/beans

        # Calculate weekly savings
        meat_per_meal = 0.2  # kg
        weekly_meat_co2 = meat_meals_per_week * meat_per_meal * beef_co2
        weekly_plant_co2 = meat_meals_per_week * meat_per_meal * plant_based_co2
        weekly_savings = weekly_meat_co2 - weekly_plant_co2

        # Annual savings
        annual_savings = weekly_savings * weeks

        return {
            'scenario': f'Replace {meat_meals_per_week} meat meals/week with plant-based',
            'weekly_savings': round(weekly_savings, 2),
            'annual_savings': round(annual_savings, 2),
            'meat_co2_per_week': round(weekly_meat_co2, 2),
            'plant_co2_per_week': round(weekly_plant_co2, 2)
        }

    def simulate_transport_switch(self, trips_per_year, distance_per_trip_km, from_mode='flight', to_mode='train'):
        """
        Simulate switching from one transport mode to another for short trips.
        """
        if from_mode not in self.transport_factors or to_mode not in self.transport_factors:
            raise ValueError(f'Unsupported transport mode. Available: {list(self.transport_factors.keys())}')

        from_co2_per_km = self.transport_factors[from_mode]
        to_co2_per_km = self.transport_factors[to_mode]

        # Calculate annual emissions
        original_annual_co2 = trips_per_year * distance_per_trip_km * from_co2_per_km
        new_annual_co2 = trips_per_year * distance_per_trip_km * to_co2_per_km
        annual_savings = original_annual_co2 - new_annual_co2

        return {
            'scenario': f'Switch from {from_mode} to {to_mode} for {trips_per_year} trips/year ({distance_per_trip_km}km each)',
            'annual_savings': round(annual_savings, 2),
            'original_annual_co2': round(original_annual_co2, 2),
            'new_annual_co2': round(new_annual_co2, 2)
        }

# Offset conversion constants
CO2_PER_TREE_PER_YEAR = 21  # kg CO2 absorbed per tree per year
TREES_PER_OFFSET_CREDIT = 1000 / CO2_PER_TREE_PER_YEAR  # ~47.6 trees per 1000kg CO2

def calculate_trees_needed(co2_amount_kg):
    """
    Calculate number of trees needed to offset a given CO2 amount.
    """
    return max(1, round(co2_amount_kg / CO2_PER_TREE_PER_YEAR))

def calculate_offset_from_trees(trees_count):
    """
    Calculate CO2 offset from a given number of trees.
    """
    return round(trees_count * CO2_PER_TREE_PER_YEAR, 2)

def get_gamification_badge(total_trees):
    """
    Return gamification badge based on total trees planted.
    """
    if total_trees >= 500:
        return {"badge": "🌳 Forest Guardian", "level": "Expert"}
    elif total_trees >= 100:
        return {"badge": "🌲 Tree Champion", "level": "Advanced"}
    elif total_trees >= 25:
        return {"badge": "🌿 Nature Protector", "level": "Intermediate"}
    elif total_trees >= 5:
        return {"badge": "🌱 Seedling Planter", "level": "Beginner"}
    else:
        return {"badge": "🌰 Future Planter", "level": "Starter"}

def calculate_eco_credits(carbon_footprint_kg):
    """
    Calculate EcoCredits earned based on carbon footprint analysis.
    Lower footprint = more credits (rewarding sustainable choices).
    """
    # Base credits for uploading receipt
    base_credits = 10

    # Bonus credits based on footprint (lower footprint = more credits)
    if carbon_footprint_kg <= 10:
        footprint_bonus = 50  # Very low footprint
    elif carbon_footprint_kg <= 25:
        footprint_bonus = 30  # Low footprint
    elif carbon_footprint_kg <= 50:
        footprint_bonus = 20  # Moderate footprint
    elif carbon_footprint_kg <= 100:
        footprint_bonus = 10  # High footprint
    else:
        footprint_bonus = 5   # Very high footprint

    return base_credits + footprint_bonus

def get_credits_needed_for_tree():
    """
    Returns the number of EcoCredits needed to plant one tree.
    """
    return 100  # 100 credits = 1 tree
