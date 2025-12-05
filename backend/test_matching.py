import sys
import os
sys.path.append('app')

from enhanced_footprint import EnhancedFootprintMatcher
from footprint import load_dataset

def test_matching():
    """Test the enhanced matching system."""
    print("🔍 Testing Enhanced CarbonDrop Matching Performance")
    print("=" * 60)

    # Load the enhanced dataset
    try:
        dataset_path = os.path.join('dataset', 'defra_enhanced_emissions.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join('dataset', 'combined_food_emissions.csv')
            print(f"⚠ Enhanced dataset not found, using fallback: {dataset_path}")

        dataset = load_dataset(dataset_path)
        matcher = EnhancedFootprintMatcher(dataset)

        print(f"✅ Loaded dataset with {len(dataset)} items")
        print(f"📊 Categories: {sorted(dataset['category'].unique())}")
        print(f"📋 Sample items: {list(dataset['item'].head(10))}")

        # Test with sample items
        test_items = [
            # Common grocery items
            {'name': 'milk', 'qty': 1, 'category': 'food', 'unit': 'liter'},
            {'name': 'bread', 'qty': 1, 'category': 'food', 'unit': 'loaf'},
            {'name': 'eggs', 'qty': 6, 'category': 'food', 'unit': 'pieces'},
            {'name': 'chicken breast', 'qty': 1, 'category': 'food', 'unit': 'kg'},
            {'name': 'ground beef', 'qty': 0.5, 'category': 'food', 'unit': 'kg'},
            {'name': 'cheddar cheese', 'qty': 0.2, 'category': 'food', 'unit': 'kg'},
            {'name': 'tomatoes', 'qty': 1, 'category': 'food', 'unit': 'kg'},
            {'name': 'potatoes', 'qty': 2, 'category': 'food', 'unit': 'kg'},
            {'name': 'apples', 'qty': 3, 'category': 'food', 'unit': 'pieces'},
            {'name': 'bananas', 'qty': 4, 'category': 'food', 'unit': 'pieces'},

            # Transport items
            {'name': 'taxi ride', 'qty': 1, 'category': 'transport', 'unit': 'trip'},
            {'name': 'bus ticket', 'qty': 1, 'category': 'transport', 'unit': 'ticket'},
            {'name': 'train journey', 'qty': 1, 'category': 'transport', 'unit': 'trip'},
            {'name': 'flight', 'qty': 1, 'category': 'transport', 'unit': 'flight'},

            # Energy items
            {'name': 'electricity', 'qty': 100, 'category': 'energy', 'unit': 'kwh'},
            {'name': 'natural gas', 'qty': 50, 'category': 'energy', 'unit': 'kwh'},
            {'name': 'water', 'qty': 1000, 'category': 'utility', 'unit': 'liter'},
        ]

        print(f"\n🧪 Testing {len(test_items)} sample items...")
        print("\n📋 Detailed Results:")
        print("-" * 100)
        print(f"{'Item'"<18"} {'Category'"<10"} {'Matched'"<25"} {'Score'"<8"} {'Footprint'"<12"} {'Status'"<10"}")
        print("-" * 100)

        matched_count = 0
        total_count = len(test_items)

        for item in test_items:
            results, total = matcher.match_and_compute([item])

            if results and results[0]['matched_name'] and results[0]['matched_name'] != 'No match':
                matched_count += 1
                match_info = results[0]
                status = "✅ Matched"
                print(f"{item['name']:<18} {item['category']:<10} {match_info['matched_name'][:23]:<25} {match_info['match_score']:<8} {match_info['footprint']:<12.2f} {status:<10}")
            else:
                status = "❌ No match"
                print(f"{item['name']:<18} {item['category']:<10} {'No match':<25} {'0':<8} {'0.00':<12} {status:<10}")

        match_rate = (matched_count / total_count) * 100
        print("-" * 100)
        print(f"\n📊 Overall Match Rate: {match_rate:.1f}% ({matched_count}/{total_count} items)")

        if match_rate >= 80:
            print("✅ Excellent matching performance!")
        elif match_rate >= 60:
            print("🟡 Good matching performance, some items may need manual review.")
        else:
            print("❌ Matching performance needs improvement.")

        # Show category breakdown
        print("\n📈 Category Breakdown:")
        categories = {}
        for item in test_items:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in categories.items():
            cat_items = [item for item in test_items if item['category'] == cat]
            cat_matched = 0
            for item in cat_items:
                results, _ = matcher.match_and_compute([item])
                if results and results[0]['matched_name'] and results[0]['matched_name'] != 'No match':
                    cat_matched += 1

            cat_rate = (cat_matched / count) * 100 if count > 0 else 0
            status = "✅" if cat_rate >= 80 else "🟡" if cat_rate >= 60 else "❌"
            print(f"   {status} {cat.capitalize()}: {cat_rate:.1f}% ({cat_matched}/{count})")

        print("\n💡 Tips for better matching:")
        print("   • Lower match scores (< 60%) indicate poor matches")
        print("   • Items with 'No match' are not found in the database")
        print("   • Consider adding missing items to the emission database")
        print("   • Check OCR extraction quality for scanned items")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Make sure the enhanced dataset exists in the dataset folder")
        return False

    return True

if __name__ == "__main__":
    test_matching()
