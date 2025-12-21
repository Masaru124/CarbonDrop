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
    """Load the comprehensive multi-domain emission dataset."""
    if not os.path.exists(csv_path):
        # Try fallback paths in order of preference
        fallback_paths = [
            os.path.join(os.path.dirname(csv_path), 'defra_enhanced_emissions.csv'),
            os.path.join(os.path.dirname(csv_path), 'combined_food_emissions.csv'),
            os.path.join(os.path.dirname(csv_path), 'greenhouse-gas-emissions-per-kilogram-of-food-product.csv')
        ]

        for fallback in fallback_paths:
            if os.path.exists(fallback):
                print(f"Using fallback dataset: {fallback}")
                csv_path = fallback
                break
        else:
            raise FileNotFoundError(f'No dataset found in any of the expected locations')

    # Load the dataset
    df = pd.read_csv(csv_path)

    print(f"Loaded dataset from {csv_path}")
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Check if this is the comprehensive multi-domain dataset
    if 'item' in df.columns and 'co2' in df.columns and 'category' in df.columns:
        print("✅ Comprehensive multi-domain dataset detected")
        # Already in the correct format
        df['item'] = df['item'].astype(str).str.strip()
        return df

    # Handle legacy food-only datasets
    print("📦 Legacy food dataset detected, converting to multi-domain format...")

    # Try to identify the correct columns
    item_col = None
    emission_col = None

    for col in df.columns:
        col_lower = col.lower()
        # Check for item/product column - expanded to include 'entity' as a fallback
        if any(keyword in col_lower for keyword in ['item', 'product', 'food', 'name', 'entity']) and item_col is None:
            item_col = col
        # Check for emission column
        if any(keyword in col_lower for keyword in ['emission', 'co2', 'footprint', 'carbon']) and emission_col is None:
            emission_col = col

    # If we couldn't find an item column, use the first non-numeric column
    if not item_col:
        for col in df.columns:
            if df[col].dtype == 'object' and col.lower() not in ['year', 'date']:
                item_col = col
                break

    # If we couldn't find an emission column, use the first numeric column
    if not emission_col:
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) and col.lower() not in ['year', 'date']:
                emission_col = col
                break

    if item_col and emission_col:
        # Convert to standard format
        df = df.rename(columns={
            item_col: 'item',
            emission_col: 'co2'
        })

        # Add missing columns
        df['unit'] = 'kg'  # Default unit
        df['category'] = 'food'  # Default category
        df['source'] = 'Legacy Dataset'

        # Clean data
        df['item'] = df['item'].astype(str).str.strip()
        df = df.dropna(subset=['co2'])
        df = df[df['co2'] > 0]

        print(f"✅ Converted legacy dataset: {len(df)} items")
        return df
    else:
        raise ValueError(f"Could not identify item and emission columns in dataset. Available columns: {list(df.columns)}")

class WhatIfSimulator:
    def __init__(self, dataset_df):
        self.df = dataset_df.copy()

        # Enhanced transport emission factors from DEFRA
        self.transport_factors = {
            'flight': 0.25,  # kg CO2e per km for short flights (average)
            'train': 0.04,   # kg CO2e per km for train (average)
            'bus': 0.08,     # kg CO2e per km for bus
            'car': 0.17,     # kg CO2e per km for average car
            'taxi': 0.17,    # kg CO2e per km for taxi
            'electric_car': 0.054,  # kg CO2e per km for electric car
        }

        # Enhanced energy factors from DEFRA
        self.energy_factors = {
            'electricity': 0.207,  # kg CO2e per kWh
            'natural_gas': 0.184,  # kg CO2e per kWh
            'gas': 0.184,          # kg CO2e per kWh
            'fuel_oil': 0.246,     # kg CO2e per kWh
            'lpg': 0.215,          # kg CO2e per kWh
            'coal': 0.345,         # kg CO2e per kWh
        }

        # Water factors
        self.water_factors = {
            'water': 0.0013,  # kg CO2e per liter (supply + treatment)
        }

    def _get_emission_factor(self, item_name, category='food'):
        """Get emission factor from the dataset."""
        # Look for exact match first
        matches = self.df[(self.df['item'].str.lower() == item_name.lower()) &
                         (self.df['category'] == category)]

        if not matches.empty:
            return float(matches.iloc[0]['co2'])

        # Look for partial matches
        matches = self.df[self.df['item'].str.lower().str.contains(item_name.lower()) &
                         (self.df['category'] == category)]

        if not matches.empty:
            return float(matches.iloc[0]['co2'])

        return None

    def simulate_meat_replacement(self, meat_meals_per_week, weeks=52):
        """
        Simulate replacing meat meals with plant-based alternatives.
        Assumes average meat meal is 200g beef, replaced with 200g lentils.
        """
        # Get CO2 for beef (meat)
        beef_co2 = self._get_emission_factor('beef', 'food')
        if beef_co2 is None:
            beef_co2 = 27.0  # Default value from dataset

        # Get CO2 for plant-based alternative (lentils)
        lentils_co2 = self._get_emission_factor('lentils', 'food')
        if lentils_co2 is None:
            lentils_co2 = 0.9  # Default value for lentils

        # Calculate weekly savings
        meat_per_meal = 0.2  # kg
        weekly_meat_co2 = meat_meals_per_week * meat_per_meal * beef_co2
        weekly_plant_co2 = meat_meals_per_week * meat_per_meal * lentils_co2
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

    def simulate_energy_efficiency(self, current_bulbs, led_bulbs, hours_per_day=4, days_per_year=365):
        """
        Simulate switching from incandescent to LED bulbs.
        """
        # Energy consumption in kWh per year
        incandescent_wattage = 60  # watts per bulb
        led_wattage = 9  # watts per bulb
        kwh_per_watt_hour = 0.001  # conversion factor

        current_annual_kwh = current_bulbs * incandescent_wattage * hours_per_day * days_per_year * kwh_per_watt_hour
        new_annual_kwh = led_bulbs * led_wattage * hours_per_day * days_per_year * kwh_per_watt_hour
        annual_savings_kwh = current_annual_kwh - new_annual_kwh

        # CO2 emissions: ~0.4 kg CO2 per kWh (average grid mix)
        co2_per_kwh = 0.4
        annual_co2_savings = annual_savings_kwh * co2_per_kwh

        return {
            'scenario': f'Switch {current_bulbs} incandescent bulbs to {led_bulbs} LED bulbs',
            'annual_energy_savings': round(annual_savings_kwh, 2),
            'annual_co2_savings': round(annual_co2_savings, 2),
            'current_annual_kwh': round(current_annual_kwh, 2),
            'new_annual_kwh': round(new_annual_kwh, 2)
        }

    def simulate_electric_vehicle(self, annual_km, current_fuel_efficiency=10, ev_efficiency=0.2):
        """
        Simulate switching from gasoline car to electric vehicle.
        """
        # Fuel efficiency: L/100km for gas car, kWh/km for EV
        # CO2 emissions: ~2.3 kg CO2 per liter of gasoline
        co2_per_liter_gas = 2.3

        # Calculate annual fuel consumption and emissions
        current_fuel_liters = (annual_km / 100) * current_fuel_efficiency
        current_annual_co2 = current_fuel_liters * co2_per_liter_gas

        # EV energy consumption and emissions (assuming grid electricity)
        new_annual_kwh = annual_km * ev_efficiency
        new_annual_co2 = new_annual_kwh * 0.4  # kg CO2 per kWh
        annual_co2_savings = current_annual_co2 - new_annual_co2

        return {
            'scenario': f'Switch to electric vehicle for {annual_km} km/year',
            'annual_co2_savings': round(annual_co2_savings, 2),
            'current_annual_co2': round(current_annual_co2, 2),
            'new_annual_co2': round(new_annual_co2, 2),
            'current_fuel_liters': round(current_fuel_liters, 2),
            'new_annual_kwh': round(new_annual_kwh, 2)
        }

    def simulate_local_food(self, imported_meals_per_week, local_reduction_percent=50, weeks=52):
        """
        Simulate choosing local/seasonal food over imported food.
        """
        # Average CO2 impact: imported food travels ~2500km vs local food ~100km
        # Transport CO2: ~0.1 kg CO2 per ton-km
        imported_distance = 2500  # km
        local_distance = 100  # km

        # Assume average meal has 0.5kg of food transported
        food_per_meal = 0.5  # kg
        meals_reduced = imported_meals_per_week * (local_reduction_percent / 100)

        current_weekly_co2 = (imported_meals_per_week * food_per_meal * imported_distance * 0.1) / 1000
        new_weekly_co2 = (meals_reduced * food_per_meal * local_distance * 0.1) / 1000
        weekly_savings = current_weekly_co2 - new_weekly_co2
        annual_savings = weekly_savings * weeks

        return {
            'scenario': f'Reduce imported food by {local_reduction_percent}% ({imported_meals_per_week} meals/week)',
            'weekly_co2_savings': round(weekly_savings, 2),
            'annual_co2_savings': round(annual_savings, 2),
            'current_weekly_co2': round(current_weekly_co2, 2),
            'new_weekly_co2': round(new_weekly_co2, 2)
        }

    def simulate_waste_reduction(self, current_waste_kg_per_week, reduction_percent=30, weeks=52):
        """
        Simulate reducing food waste.
        """
        # CO2 impact of food waste: ~3.5 kg CO2 per kg of food waste
        co2_per_kg_waste = 3.5

        current_annual_waste = current_waste_kg_per_week * weeks
        reduced_waste = current_waste_kg_per_week * (reduction_percent / 100)
        new_annual_waste = current_annual_waste - reduced_waste * weeks

        current_annual_co2 = current_annual_waste * co2_per_kg_waste
        new_annual_co2 = new_annual_waste * co2_per_kg_waste
        annual_co2_savings = current_annual_co2 - new_annual_co2

        return {
            'scenario': f'Reduce food waste by {reduction_percent}% ({current_waste_kg_per_week} kg/week)',
            'annual_waste_reduction': round(reduced_waste * weeks, 2),
            'annual_co2_savings': round(annual_co2_savings, 2),
            'current_annual_co2': round(current_annual_co2, 2),
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
