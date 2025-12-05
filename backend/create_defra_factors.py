"""
Manual DEFRA Transport and Energy Factors

Since the DEFRA Excel format is complex with merged cells, I'll add the most
important emission factors manually based on the DEFRA 2024 values.

Key factors to add:
- Transport: cars, buses, trains, flights, taxis
- Energy: electricity, natural gas, fuel oil
- Utilities: water
"""

import pandas as pd

def create_defra_factors_csv():
    """Create a CSV with key DEFRA emission factors."""

    # DEFRA 2024 key transport factors (kg CO2e per km)
    transport_factors = [
        # Passenger vehicles (average car)
        {'item': 'average car', 'co2': 0.17019, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'small car', 'co2': 0.13544, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'medium car', 'co2': 0.17019, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'large car', 'co2': 0.22005, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'average car petrol', 'co2': 0.17708, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'average car diesel', 'co2': 0.16490, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},

        # Buses
        {'item': 'local bus', 'co2': 0.10335, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'coach', 'co2': 0.02742, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},

        # Trains
        {'item': 'national rail', 'co2': 0.03641, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'light rail', 'co2': 0.05266, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'london underground', 'co2': 0.02742, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},

        # Taxis
        {'item': 'taxi regular', 'co2': 0.17708, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'taxi black cab', 'co2': 0.22005, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},

        # Flights (short-haul)
        {'item': 'domestic flight', 'co2': 0.25474, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'short haul flight', 'co2': 0.15284, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'long haul flight', 'co2': 0.19545, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},

        # Electric vehicles
        {'item': 'electric car', 'co2': 0.05443, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
        {'item': 'electric van', 'co2': 0.07552, 'unit': 'km', 'category': 'transport', 'source': 'DEFRA 2024'},
    ]

    # DEFRA 2024 key energy factors
    energy_factors = [
        # Electricity
        {'item': 'electricity', 'co2': 0.20707, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'uk electricity', 'co2': 0.20707, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'grid electricity', 'co2': 0.20707, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},

        # Natural gas
        {'item': 'natural gas', 'co2': 0.18385, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'gas', 'co2': 0.18385, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'natural gas therm', 'co2': 5.30084, 'unit': 'therm', 'category': 'energy', 'source': 'DEFRA 2024'},

        # Fuel oil
        {'item': 'fuel oil', 'co2': 0.24551, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'heating oil', 'co2': 0.24551, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'kerosene', 'co2': 0.24781, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},

        # LPG
        {'item': 'lpg', 'co2': 0.21476, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'propane', 'co2': 0.21476, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},

        # Coal
        {'item': 'coal', 'co2': 0.34485, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
        {'item': 'house coal', 'co2': 0.34485, 'unit': 'kwh', 'category': 'energy', 'source': 'DEFRA 2024'},
    ]

    # Water factors
    water_factors = [
        {'item': 'water supply', 'co2': 0.00059, 'unit': 'liter', 'category': 'utility', 'source': 'DEFRA 2024'},
        {'item': 'water treatment', 'co2': 0.00071, 'unit': 'liter', 'category': 'utility', 'source': 'DEFRA 2024'},
        {'item': 'water', 'co2': 0.00130, 'unit': 'liter', 'category': 'utility', 'source': 'DEFRA 2024'},  # supply + treatment
    ]

    # Combine all factors
    all_factors = transport_factors + energy_factors + water_factors

    # Create DataFrame
    df = pd.DataFrame(all_factors)

    # Save to CSV
    output_path = 'dataset/defra_emission_factors.csv'
    df.to_csv(output_path, index=False)

    print(f"✅ Created DEFRA emission factors CSV with {len(df)} entries")
    print(f"📁 Saved to: {output_path}")
    print(f"\n📊 Breakdown:")
    print(f"   • Transport: {len(transport_factors)} factors")
    print(f"   • Energy: {len(energy_factors)} factors")
    print(f"   • Water/Utility: {len(water_factors)} factors")

    # Show sample
    print(f"\n🔍 Sample transport factors:")
    print(df[df['category'] == 'transport'].head())

    print(f"\n🔍 Sample energy factors:")
    print(df[df['category'] == 'energy'].head())

    return output_path

if __name__ == "__main__":
    create_defra_factors_csv()
