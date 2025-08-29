import sys
import os
sys.path.append('app')

from ocr import extract_items_from_image
from footprint import FootprintMatcher, load_dataset

def test_matching():
    # Load the dataset
    dataset_path = os.path.join('dataset', 'greenhouse-gas-emissions-per-kilogram-of-food-product.csv')
    dataset = load_dataset(dataset_path)
    matcher = FootprintMatcher(dataset)
    
    print("Dataset items:", list(dataset['item']))
    print("-" * 50)
    
    # Test with sample receipt
    sample_receipt_path = os.path.join('sample_receipts', 'basic-receipt.png')
    
    with open(sample_receipt_path, 'rb') as f:
        image_bytes = f.read()
    
    print("Testing OCR extraction...")
    items = extract_items_from_image(image_bytes)
    print(f"Extracted items: {items}")
    print("-" * 50)
    
    print("Testing matching...")
    results, total = matcher.match_and_compute(items)
    print(f"Matching results: {results}")
    print(f"Total footprint: {total}")

if __name__ == "__main__":
    test_matching()
