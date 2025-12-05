"""
DEFRA GHG Conversion Factors Integration

This script downloads and processes the UK Government's GHG conversion factors
from the official DEFRA publication. These factors are widely used and provide
comprehensive emission factors for transport, energy, and other activities.

Source: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024
"""

import pandas as pd
import requests
import os
import zipfile
import tempfile
from pathlib import Path

class DEFRAIntegrator:
    """Handles downloading and processing DEFRA GHG conversion factors."""

    def __init__(self, output_dir="dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # DEFRA 2024 conversion factors URL (update annually)
        self.base_url = "https://assets.publishing.service.gov.uk/media/"
        self.zip_filename = "ghg-conversion-factors-2024-condensed_set__for_most_users__v1_1.xlsx"

    def download_defra_data(self):
        """Download DEFRA conversion factors Excel file."""
        print("Downloading DEFRA GHG conversion factors...")

        # Full URL for 2024 factors
        url = f"{self.base_url}6722566a3758e4604742aa1e/{self.zip_filename}"

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            print(f"✓ Downloaded DEFRA data to {tmp_path}")
            return tmp_path

        except requests.RequestException as e:
            print(f"✗ Failed to download DEFRA data: {e}")
            return None

    def extract_transport_factors(self, excel_file):
        """Extract transport emission factors from DEFRA Excel."""
        print("Extracting transport emission factors...")

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file, sheet_name=None)

            # Print available sheets for debugging
            print(f"Available sheets: {list(df.keys())}")

            # Look for transport-related sheets (more flexible matching)
            transport_sheets = []
            for name in df.keys():
                name_lower = name.lower()
                if any(keyword in name_lower for keyword in ['vehicle', 'car', 'bus', 'train', 'flight', 'transport', 'passenger']):
                    transport_sheets.append(name)

            if not transport_sheets:
                print("⚠ No transport-related sheets found")
                # Try all sheets as fallback
                transport_sheets = list(df.keys())

            transport_factors = []

            for sheet_name in transport_sheets:
                print(f"Processing sheet: {sheet_name}")
                sheet_df = df[sheet_name]

                # Print column names for debugging
                print(f"Columns in {sheet_name}: {list(sheet_df.columns)}")

                # Look for emission factor patterns in columns
                factor_columns = []
                for col in sheet_df.columns:
                    col_str = str(col).lower()
                    if any(keyword in col_str for keyword in ['kg co2e', 'kgco2e', 'emission', 'factor']):
                        factor_columns.append(col)

                print(f"Potential factor columns in {sheet_name}: {factor_columns}")

                # Process each row
                for idx, row in sheet_df.iterrows():
                    # Skip header rows (look for 'Unit' or 'Scope' in first column)
                    first_col = str(row.iloc[0]).strip() if len(row) > 0 else ""
                    if pd.isna(row.iloc[0]) or first_col.lower() in ['unit', 'scope', 'factor', '', 'nan']:
                        continue

                    try:
                        # Extract vehicle/item type
                        vehicle_type = first_col.strip()
                        if not vehicle_type:
                            continue

                        # Look for emission factors in identified columns
                        for col in factor_columns:
                            if col in sheet_df.columns and not pd.isna(row[col]):
                                try:
                                    factor_value = float(row[col])

                                    # Determine unit from column name or context
                                    col_name = str(col).lower()
                                    if 'per km' in col_name or 'km' in col_name:
                                        unit = 'km'
                                    elif 'per passenger' in col_name:
                                        unit = 'passenger_km'
                                    else:
                                        unit = 'unit'

                                    transport_factors.append({
                                        'item': vehicle_type.lower(),
                                        'co2': factor_value,
                                        'unit': unit,
                                        'category': 'transport',
                                        'source': 'DEFRA 2024',
                                        'sheet': sheet_name
                                    })
                                    break  # Only take first matching factor per row

                                except (ValueError, TypeError):
                                    continue

                    except (IndexError, AttributeError):
                        continue

            result_df = pd.DataFrame(transport_factors)
            if not result_df.empty:
                print(f"✓ Extracted {len(result_df)} transport factors from sheets: {[s for s in transport_sheets if s in list(df.keys())]}")
                # Show sample of extracted data
                print("Sample transport factors:")
                print(result_df.head())
                return result_df
            else:
                print("⚠ No transport factors extracted")
                return pd.DataFrame()

        except Exception as e:
            print(f"✗ Error extracting transport factors: {e}")
            return pd.DataFrame()

    def extract_energy_factors(self, excel_file):
        """Extract energy emission factors from DEFRA Excel."""
        print("Extracting energy emission factors...")

        try:
            df = pd.read_excel(excel_file, sheet_name=None)

            # Look for energy-related sheets (more flexible matching)
            energy_sheets = []
            for name in df.keys():
                name_lower = name.lower()
                if any(keyword in name_lower for keyword in ['energy', 'electric', 'fuel', 'gas', 'power', 'kwh', 'therm']):
                    energy_sheets.append(name)

            if not energy_sheets:
                print("⚠ No energy-related sheets found")
                # Try all sheets as fallback (excluding already processed transport sheets)
                processed_sheets = set()
                energy_sheets = [name for name in df.keys() if name not in processed_sheets]

            energy_factors = []

            for sheet_name in energy_sheets:
                print(f"Processing energy sheet: {sheet_name}")
                sheet_df = df[sheet_name]

                # Print column names for debugging
                print(f"Columns in {sheet_name}: {list(sheet_df.columns)}")

                # Look for emission factor patterns in columns
                factor_columns = []
                for col in sheet_df.columns:
                    col_str = str(col).lower()
                    if any(keyword in col_str for keyword in ['kg co2e', 'kgco2e', 'emission', 'factor']):
                        factor_columns.append(col)

                print(f"Potential factor columns in {sheet_name}: {factor_columns}")

                # Process each row
                for idx, row in sheet_df.iterrows():
                    # Skip header rows
                    first_col = str(row.iloc[0]).strip() if len(row) > 0 else ""
                    if pd.isna(row.iloc[0]) or first_col.lower() in ['unit', 'scope', 'factor', '', 'nan']:
                        continue

                    try:
                        # Extract fuel/energy type
                        energy_type = first_col.strip()
                        if not energy_type:
                            continue

                        # Look for emission factors in identified columns
                        for col in factor_columns:
                            if col in sheet_df.columns and not pd.isna(row[col]):
                                try:
                                    factor_value = float(row[col])

                                    # Determine unit from column name or context
                                    col_name = str(col).lower()
                                    if 'per kwh' in col_name or 'kwh' in col_name:
                                        unit = 'kwh'
                                    elif 'per therm' in col_name or 'therm' in col_name:
                                        unit = 'therm'
                                    elif 'per liter' in col_name or 'liter' in col_name:
                                        unit = 'liter'
                                    elif 'per gallon' in col_name or 'gallon' in col_name:
                                        unit = 'gallon'
                                    else:
                                        unit = 'unit'

                                    energy_factors.append({
                                        'item': energy_type.lower(),
                                        'co2': factor_value,
                                        'unit': unit,
                                        'category': 'energy',
                                        'source': 'DEFRA 2024',
                                        'sheet': sheet_name
                                    })
                                    break  # Only take first matching factor per row

                                except (ValueError, TypeError):
                                    continue

                    except (IndexError, AttributeError):
                        continue

            result_df = pd.DataFrame(energy_factors)
            if not result_df.empty:
                print(f"✓ Extracted {len(result_df)} energy factors")
                # Show sample of extracted data
                print("Sample energy factors:")
                print(result_df.head())
                return result_df
            else:
                print("⚠ No energy factors extracted")
                return pd.DataFrame()

        except Exception as e:
            print(f"✗ Error extracting energy factors: {e}")
            return pd.DataFrame()

    def create_unified_dataset(self, transport_df, energy_df, existing_df=None):
        """Combine DEFRA factors with existing dataset."""
        print("Creating unified emission factor dataset...")

        combined_dfs = []

        # Add existing data if provided and not empty
        if existing_df is not None and not existing_df.empty:
            print(f"✓ Adding {len(existing_df)} existing food entries")

            # Normalize existing dataset to match DEFRA format
            existing_normalized = self._normalize_existing_dataset(existing_df)
            combined_dfs.append(existing_normalized)

        # Add DEFRA transport factors if not empty
        if not transport_df.empty:
            print(f"✓ Adding {len(transport_df)} transport entries")
            combined_dfs.append(transport_df)

        # Add DEFRA energy factors if not empty
        if not energy_df.empty:
            print(f"✓ Adding {len(energy_df)} energy entries")
            combined_dfs.append(energy_df)

        if combined_dfs:
            unified_df = pd.concat(combined_dfs, ignore_index=True)

            # Only drop duplicates if we have the required columns
            if 'item' in unified_df.columns:
                # For food items, deduplicate by item name only (not category, since food items might have same names)
                food_items = unified_df[unified_df['category'] == 'food']
                non_food_items = unified_df[unified_df['category'] != 'food']

                if not food_items.empty:
                    food_items = food_items.drop_duplicates(subset=['item'], keep='first')
                if not non_food_items.empty:
                    non_food_items = non_food_items.drop_duplicates(subset=['item', 'category'], keep='first')

                unified_df = pd.concat([food_items, non_food_items], ignore_index=True)
                print(f"✓ After deduplication: {len(unified_df)} total entries")
                print(f"   • Food items: {len(food_items)}")
                print(f"   • Non-food items: {len(non_food_items)}")
            else:
                print(f"⚠ Could not deduplicate (missing 'item' column), dataset has {len(unified_df)} entries")

            return unified_df
        else:
            print("⚠ No data to combine")
            return existing_df

    def _normalize_existing_dataset(self, existing_df):
        """Normalize existing food dataset to match DEFRA format."""
        # Check what columns exist in the existing dataset
        print(f"Existing dataset columns: {list(existing_df.columns)}")

        # Try to find the item name and emission factor columns
        item_col = None
        emission_col = None
        unit_col = None

        # Common column name patterns
        for col in existing_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['item', 'product', 'food', 'name']) and item_col is None:
                item_col = col
            if any(keyword in col_lower for keyword in ['emission', 'co2', 'footprint', 'carbon']) and emission_col is None:
                emission_col = col
            if any(keyword in col_lower for keyword in ['unit', 'per']) and unit_col is None:
                unit_col = col

        if item_col and emission_col:
            print(f"Found columns - Item: {item_col}, Emission: {emission_col}")

            # Create normalized dataframe
            normalized = pd.DataFrame({
                'item': existing_df[item_col].astype(str).str.strip().str.lower(),
                'co2': pd.to_numeric(existing_df[emission_col], errors='coerce'),
                'unit': existing_df.get(unit_col, 'kg') if unit_col else 'kg',
                'category': 'food',
                'source': 'Existing Dataset'
            })

            # Drop rows with missing emission values
            normalized = normalized.dropna(subset=['co2'])
            normalized = normalized[normalized['co2'] > 0]

            print(f"✓ Normalized {len(normalized)} food entries")
            return normalized
        else:
            print(f"⚠ Could not find required columns in existing dataset")
            print(f"   Available columns: {list(existing_df.columns)}")
            return pd.DataFrame()

    def load_manual_defra_factors(self):
        """Load manually created DEFRA factors."""
        factors_path = self.output_dir / "defra_emission_factors.csv"
        if factors_path.exists():
            print(f"Loading manual DEFRA factors from {factors_path}")
            return pd.read_csv(factors_path)
        else:
            print(f"⚠ Manual DEFRA factors not found at {factors_path}")
            print("Run 'python create_defra_factors.py' first")
            return pd.DataFrame()

    def run_integration(self, existing_dataset_path=None):
        """Run the complete DEFRA integration process."""
        print("🚀 Starting DEFRA GHG Conversion Factors Integration")
        print("=" * 60)

        # First create manual DEFRA factors
        print("Creating manual DEFRA factors...")
        from create_defra_factors import create_defra_factors_csv
        factors_path = create_defra_factors_csv()

        # Load the factors
        defra_df = self.load_manual_defra_factors()

        # Load existing dataset if provided
        existing_df = None
        if existing_dataset_path and os.path.exists(existing_dataset_path):
            print(f"Loading existing dataset from {existing_dataset_path}")
            existing_df = pd.read_csv(existing_dataset_path)

        # Create unified dataset
        unified_df = self.create_unified_dataset(pd.DataFrame(), defra_df, existing_df)

        if unified_df is not None:
            # Save to output directory
            output_path = self.output_dir / "defra_enhanced_emissions.csv"
            unified_df.to_csv(output_path, index=False)
            print(f"💾 Saved enhanced dataset to {output_path}")

            # Show summary
            print("\n📊 Dataset Summary:")
            if existing_df is not None and not existing_df.empty:
                print(f"   • Original food items: {len(existing_df)}")
            print(f"   • DEFRA transport factors: {len(defra_df[defra_df['category'] == 'transport'])}")
            print(f"   • DEFRA energy factors: {len(defra_df[defra_df['category'] == 'energy'])}")
            print(f"   • DEFRA utility factors: {len(defra_df[defra_df['category'] == 'utility'])}")
            print(f"   • Total unique items: {len(unified_df)}")

            print("\n✅ DEFRA integration completed successfully!")
            return output_path

        return None

def main():
    """Main function to run DEFRA integration."""
    integrator = DEFRAIntegrator()

    # Path to existing dataset (if any)
    existing_path = "dataset/combined_food_emissions.csv"

    result_path = integrator.run_integration(existing_path)
    if result_path:
        print(f"\n🎉 Integration successful! Enhanced dataset available at: {result_path}")
    else:
        print("\n❌ Integration failed. Check the errors above.")

if __name__ == "__main__":
    main()
