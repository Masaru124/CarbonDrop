import pandas as pd
import numpy as np

# Read the CSVs
food_df = pd.read_csv('dataset/food.csv')
greenhouse_df = pd.read_csv('dataset/greenhouse-gas-emissions-per-kilogram-of-food-product.csv')
footprint_df = pd.read_csv('dataset/footprint.csv')

# The food.csv does not have 'product_name' or 'energy_100g' columns, so skip dropna on those columns

# Standardize categories: use Category column, take first category if multiple
food_df['main_category'] = food_df['Category'].str.split(',').str[0].str.strip().str.lower()

# Clean main_category by removing 'en:' prefix
food_df['main_category'] = food_df['main_category'].str.replace(r'^en:', '', regex=True).str.strip()

# Clean greenhouse: create dict
greenhouse_dict = dict(zip(greenhouse_df['Entity'].str.lower(), greenhouse_df['GHG emissions per kilogram (Poore & Nemecek, 2018)']))

# Clean footprint: convert to per kg
footprint_dict = {}
for _, row in footprint_df.iterrows():
    item = row['item'].lower()
    unit = row['unit']
    co2 = row['co2']
    if unit == 'kg':
        footprint_dict[item] = co2
    elif unit == 'L':
        # Assume density 1.03 kg/L for milk
        footprint_dict[item] = co2 * 1.03
    elif unit == 'pcs':
        # Assume avg weight: eggs 50g, others ? but only eggs
        if item == 'eggs':
            footprint_dict[item] = co2 / 0.05  # per kg

# Mapping dict for categories to greenhouse/footprint
category_mapping = {
    'beef': 'beef (beef herd)',
    'lamb': 'lamb & mutton',
    'pork': 'pig meat',
    'chicken': 'poultry meat',
    'milk': 'milk',
    'eggs': 'eggs',
    'cheese': 'cheese',
    'rice': 'rice',
    'potatoes': 'potatoes',
    'tomatoes': 'tomatoes',
    'bread': 'wheat & rye',  # approx
    'coffee': 'coffee',
    'tea': 'other',  # no match
    'sugar': 'cane sugar',  # approx
    'fish': 'fish (farmed)',
    'butter': 'milk',  # approx
    'yogurt': 'milk',
    'apples': 'apples',
    'bananas': 'bananas',
    'barley': 'barley',
    'berries': 'berries & grapes',
    'cassava': 'cassava',
    'citrus': 'citrus fruit',
    'dark chocolate': 'dark chocolate',
    'groundnuts': 'groundnuts',
    'maize': 'maize',
    'nuts': 'nuts',
    'oatmeal': 'oatmeal',
    'onions': 'onions & leeks',
    'peas': 'peas',
    'prawns': 'prawns (farmed)',
    'root vegetables': 'root vegetables',
    'soy milk': 'soy milk',
    'tofu': 'tofu',
    'wine': 'wine',
    # Add more as needed
}

# Function to get emission
def get_emission(category):
    cat = category.lower()
    if cat in greenhouse_dict:
        return greenhouse_dict[cat]
    elif cat in footprint_dict:
        return footprint_dict[cat]
    # Check mapping
    for key, val in category_mapping.items():
        if key in cat:
            if val in greenhouse_dict:
                return greenhouse_dict[val]
            elif val in footprint_dict:
                return footprint_dict[val]
    # Fallback: try partial match in greenhouse_dict keys
    for key in greenhouse_dict.keys():
        if key in cat or cat in key:
            return greenhouse_dict[key]
    # Fallback: try partial match in footprint_dict keys
    for key in footprint_dict.keys():
        if key in cat or cat in key:
            return footprint_dict[key]
    print(f"Missing emission for category: {category}")
    return np.nan

# Add emissions column
food_df['emissions_per_kg'] = food_df['main_category'].apply(get_emission)

# Calculate carbon footprint per 100g
food_df['carbon_footprint_per_100g'] = food_df['emissions_per_kg'] * 0.1  # 100g = 0.1 kg

# Rename Description to product_name for consistency
food_df['product_name'] = food_df['Description']

# Drop main_category if not needed
food_df = food_df.drop(columns=['main_category'])

# Write to new CSV
food_df.to_csv('dataset/combined_food_emissions.csv', index=False)

print("New CSV created: dataset/combined_food_emissions.csv")
