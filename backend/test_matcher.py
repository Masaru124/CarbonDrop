#!/usr/bin/env python3
"""Quick test of the enhanced footprint matcher."""

import sys
import pandas as pd
from app.enhanced_footprint import EnhancedFootprintMatcher
from app.footprint import load_dataset

# Load the dataset
try:
    df = load_dataset("app/dataset/greenhouse-gas-emissions-per-kilogram-of-food-product.csv")
    print(f"✅ Dataset loaded successfully with {len(df)} items")
    print(f"Columns: {list(df.columns)}")
    print(f"First few rows:")
    print(df.head())
except Exception as e:
    print(f"❌ Failed to load dataset: {e}")
    sys.exit(1)

# Create matcher
try:
    matcher = EnhancedFootprintMatcher(df)
    print(f"\n✅ Matcher created successfully")
except Exception as e:
    print(f"❌ Failed to create matcher: {e}")
    sys.exit(1)

# Test matching
test_items = [
    {'name': 'Bread', 'qty': 1.0, 'category': 'food', 'unit': 'kg'},
    {'name': 'Milk', 'qty': 1.0, 'category': 'food', 'unit': 'kg'},
    {'name': 'Chicken', 'qty': 1.0, 'category': 'food', 'unit': 'kg'},
]

try:
    results, total = matcher.match_and_compute(test_items)
    print(f"\n✅ Matching succeeded!")
    print(f"Total footprint: {total} kg CO2e")
    for result in results:
        print(f"  - {result['name']}: {result['footprint']} kg CO2e (matched: {result['matched_name']}, score: {result['match_score']})")
except Exception as e:
    print(f"❌ Failed to match items: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
