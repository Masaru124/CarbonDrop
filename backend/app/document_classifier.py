import pytesseract
from PIL import Image
import re
import io
from enum import Enum

class DocumentType(Enum):
    GROCERY = "grocery"
    RESTAURANT = "restaurant"
    UTILITY = "utility"
    INVOICE = "invoice"
    TRANSPORT = "transport"
    OTHER = "other"

def preprocess_for_classification(image_bytes: bytes) -> str:
    """Extract text from image for document classification."""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    # Use simpler preprocessing for classification
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config, lang='eng')
    return text.lower()

def classify_document(text: str) -> DocumentType:
    """
    Classify document type based on extracted text patterns.

    This classifier uses keyword matching and pattern recognition to identify
    different types of carbon footprint documents.
    """

    # Grocery receipt patterns
    grocery_keywords = [
        'grocery', 'supermarket', 'groceries', 'produce', 'dairy', 'bakery',
        'meat', 'vegetables', 'fruit', 'milk', 'bread', 'eggs', 'cheese',
        'kg', 'lb', 'lbs', 'grams', 'litre', 'liter', 'ml', 'pack', 'packet'
    ]

    # Restaurant receipt patterns
    restaurant_keywords = [
        'restaurant', 'cafe', 'diner', 'bistro', 'table', 'seat', 'server',
        'tip', 'gratuity', 'service', 'dining', 'menu', 'dish', 'course',
        'appetizer', 'entree', 'dessert', 'beverage', 'drink'
    ]

    # Utility bill patterns
    utility_keywords = [
        'electric', 'electricity', 'power', 'energy', 'gas', 'water', 'utility',
        'bill', 'invoice', 'statement', 'account', 'meter', 'reading', 'usage',
        'kwh', 'kw-h', 'therms', 'cubic', 'meter', 'gallon', 'consumption',
        'utility company', 'electric company', 'power company'
    ]

    # Invoice patterns
    invoice_keywords = [
        'invoice', 'bill', 'statement', 'payment', 'due', 'amount', 'total',
        'tax', 'vat', 'shipping', 'handling', 'discount', 'subtotal',
        'item', 'description', 'quantity', 'unit price', 'line total'
    ]

    # Transport patterns
    transport_keywords = [
        'transport', 'travel', 'flight', 'train', 'bus', 'taxi', 'uber', 'lyft',
        'ticket', 'boarding', 'passenger', 'trip', 'journey', 'distance',
        'fuel', 'gasoline', 'diesel', 'electric vehicle', 'charging'
    ]

    # Count keyword matches for each category
    grocery_score = sum(1 for keyword in grocery_keywords if keyword in text)
    restaurant_score = sum(1 for keyword in restaurant_keywords if keyword in text)
    utility_score = sum(1 for keyword in utility_keywords if keyword in text)
    invoice_score = sum(1 for keyword in invoice_keywords if keyword in text)
    transport_score = sum(1 for keyword in transport_keywords if keyword in text)

    # Additional pattern matching for better accuracy

    # Check for currency patterns (common in receipts)
    currency_patterns = re.findall(r'\$\d+\.?\d{0,2}|£\d+\.?\d{0,2}|€\d+\.?\d{0,2}', text)
    has_currency = len(currency_patterns) > 0

    # Check for date patterns
    date_patterns = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
    has_dates = len(date_patterns) > 0

    # Check for typical receipt structure (multiple items with prices)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    price_lines = sum(1 for line in lines if re.search(r'\d+\.?\d{0,2}', line))

    # Boost scores based on structural patterns
    if has_currency and price_lines > 3:
        if utility_score > 0:
            utility_score += 2
        elif restaurant_score > 0:
            restaurant_score += 2
        elif grocery_score > 0:
            grocery_score += 2

    # Determine document type based on highest score
    scores = {
        DocumentType.GROCERY: grocery_score,
        DocumentType.RESTAURANT: restaurant_score,
        DocumentType.UTILITY: utility_score,
        DocumentType.INVOICE: invoice_score,
        DocumentType.TRANSPORT: transport_score
    }

    # If no clear winner and we have typical receipt patterns, default to grocery
    if max(scores.values()) == 0 and (has_currency or price_lines > 2):
        return DocumentType.GROCERY

    return max(scores, key=scores.get)

def classify_document_from_image(image_bytes: bytes) -> DocumentType:
    """Classify document directly from image bytes."""
    text = preprocess_for_classification(image_bytes)
    return classify_document(text)
