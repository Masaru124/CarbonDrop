import sys
import os
sys.path.append('app')

from ocr import extract_items_from_image

def test_ocr_with_sample_receipt():
    # Read the sample receipt image
    sample_receipt_path = os.path.join('sample_receipts', 'basic-receipt.png')
    
    if not os.path.exists(sample_receipt_path):
        print(f"Sample receipt not found: {sample_receipt_path}")
        return
    
    with open(sample_receipt_path, 'rb') as f:
        image_bytes = f.read()
    
    print("Testing OCR with sample receipt...")
    print(f"File: {sample_receipt_path}")
    print("-" * 50)
    
    try:
        items = extract_items_from_image(image_bytes)
        
        if items:
            print(f"Successfully extracted {len(items)} items:")
            for i, item in enumerate(items, 1):
                print(f"{i}. {item['name']} (Qty: {item['qty']}, Price: ${item['price']:.2f})")
                print(f"   Raw line: {item['raw_line']}")
        else:
            print("No items extracted from the receipt.")
            
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_with_sample_receipt()
