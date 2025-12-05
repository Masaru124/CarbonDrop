import io
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from pytesseract import Output

IGNORE_KEYWORDS = {'TOTAL','SUBTOTAL','SUB-TOTAL','TAX','VAT','CHANGE','CASH','CARD','BALANCE','PAY','AMOUNT','DISCOUNT'}

PRICE_RE_END = re.compile(r'(\d{1,5}(?:[\.,]\d{2})?)\s*(?:$|[€£$]|EUR|USD|GBP)')
QTY_X_RE = re.compile(r'(\d+)\s*[xX]')
QTY_PCS_RE = re.compile(r'(\d+)\s*(?:pcs?|PK|pack)', re.I)

def preprocess_image_bytes(image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    max_side = max(img.size)
    if max_side < 1200:
        scale = 1200 / max_side
        img = img.resize((int(img.width*scale), int(img.height*scale)))
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    return Image.fromarray(th)

def clean_item_name(raw: str) -> str:
    """Enhanced item name cleaning with better normalization."""
    text = raw.lower().strip()

    # Remove common OCR artifacts and noise
    text = re.sub(r'[^\w\s\-.,]', ' ', text)  # Replace non-alphanumeric with spaces
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

    # Common OCR typo corrections and standardizations
    corrections = {
        # Common OCR errors
        'mi1k': 'milk', 'mil': 'milk', 'mik': 'milk',
        'brea': 'bread', 'bre': 'bread',
        'chic': 'chicken', 'chick': 'chicken', 'chi': 'chicken',
        'chee': 'cheese', 'ches': 'cheese',
        'toma': 'tomato', 'tomat': 'tomato',
        'pota': 'potato', 'potat': 'potato',
        'appl': 'apple', 'app': 'apple',
        'bana': 'banana', 'ban': 'banana',
        'eggi': 'eggs', 'egg': 'eggs',
        'beef': 'beef', 'bee': 'beef',
        'rice': 'rice', 'ric': 'rice',
        'past': 'pasta', 'pas': 'pasta',

        # Common variations and abbreviations
        'whole milk': 'milk', 'semi skimmed': 'milk', 'skim milk': 'milk',
        'white bread': 'bread', 'brown bread': 'bread', 'wholemeal': 'bread',
        'free range eggs': 'eggs', 'large eggs': 'eggs', 'medium eggs': 'eggs',
        'chicken breast': 'chicken', 'chicken thigh': 'chicken',
        'ground beef': 'beef', 'minced beef': 'beef', 'steak': 'beef',
        'cheddar cheese': 'cheese', 'mozzarella': 'cheese', 'parmesan': 'cheese',
        'cherry tomato': 'tomato', 'plum tomato': 'tomato',
        'baking potato': 'potato', 'new potato': 'potato',
        'braeburn apple': 'apple', 'granny smith': 'apple', 'gala apple': 'apple',
        'fairtrade banana': 'banana',
        'white rice': 'rice', 'brown rice': 'rice', 'basmati': 'rice', 'jasmine rice': 'rice',
        'spaghetti': 'pasta', 'penne': 'pasta', 'fusilli': 'pasta', 'macaroni': 'pasta',

        # Units and quantities (remove these)
        'kg': '', 'kilo': '', 'kilogram': '', 'kilograms': '',
        'g': '', 'gram': '', 'grams': '',
        'l': '', 'liter': '', 'litre': '', 'liters': '', 'litres': '',
        'ml': '', 'milliliter': '', 'millilitre': '', 'milliliters': '', 'millilitres': '',
        'lb': '', 'lbs': '', 'pound': '', 'pounds': '',
        'oz': '', 'ounce': '', 'ounces': '',
        'pack': '', 'packet': '', 'pack of': '', 'pk': '',
        'pc': '', 'piece': '', 'pieces': '', 'pcs': '',
        'ea': '', 'each': '', 'item': '',
    }

    # Apply corrections
    for wrong, correct in corrections.items():
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text)

    # Remove numbers and units that weren't caught above
    text = re.sub(r'\d+(\.\d+)?', '', text)  # Remove numbers
    text = re.sub(r'\b(?:kg|g|lb|oz|l|ml|liter|gram|pound|ounce|pack|piece|item|each)\b', '', text)

    # Clean up extra spaces and normalize
    text = re.sub(r'\s+', ' ', text).strip()

    # Skip if it's a total/subtotal keyword
    skip_keywords = ['total', 'subtotal', 'tax', 'vat', 'change', 'cash', 'card', 'balance', 'pay', 'amount', 'discount', 'tip', 'service', 'gratuity']
    if text in skip_keywords:
        return ""

    return text.capitalize()

def _reconstruct_lines(img):
    cfg = '--oem 3 --psm 6'
    df = pytesseract.image_to_data(img, output_type=Output.DATAFRAME, config=cfg, lang='eng')
    df = df.dropna(subset=['text']).copy()
    df = df[df['conf'] > 40]
    lines = []
    if df.empty:
        return lines
    for key, group in df.groupby(['page_num','block_num','par_num','line_num']):
        g = group.sort_values('left')
        text = ' '.join(str(t) for t in g['text'].tolist()).strip()
        if text:
            lines.append(text)
    return lines

def _parse_line(line: str):
    """Enhanced line parsing with better price and quantity detection."""
    raw = line.strip()
    if not raw:
        return None

    # Skip non-item lines more aggressively
    up = re.sub(r'[^A-Z ]+', '', raw.upper())
    extended_skip_keywords = {
        'TOTAL','SUBTOTAL','SUB-TOTAL','TAX','VAT','CHANGE','CASH','CARD','BALANCE','PAY',
        'AMOUNT','DISCOUNT','TIP','SERVICE','GRATUITY','TABLE','SEAT','SERVER','BILL',
        'INVOICE','RECEIPT','THANK','YOU','WELCOME','CUSTOMER','GUEST','ORDER','ITEM',
        'QTY','QUANTITY','PRICE','UNIT','RATE','DESCRIPTION','PRODUCT','NAME','NUMBER'
    }

    if any(k in up for k in extended_skip_keywords):
        return None

    # Enhanced price regex patterns
    price_patterns = [
        r'(\d{1,5}(?:[\.,]\d{2})?)\s*(?:$|[€£$]|EUR|USD|GBP)',  # Price at end
        r'(?:€|£|\$|EUR|USD|GBP)\s*(\d{1,5}(?:[\.,]\d{2})?)',    # Currency at start
        r'(\d{1,5}(?:[\.,]\d{2})?)\s*(?:€|£|\$)',                # Price with currency
    ]

    price = None
    for pattern in price_patterns:
        m = re.search(pattern, raw)
        if m:
            price_str = m.group(1).replace(',', '.')
            try:
                price = float(price_str)
                break
            except:
                continue

    if not price:
        return None

    # Extract item name (everything before the price)
    name_part = raw[:raw.find(m.group(0))].strip(' -:')

    # Enhanced quantity detection
    qty_patterns = [
        r'^(\d+)\s*[xX]\s*',  # 2x, 3x format
        r'(\d+)\s*(?:pcs?|PK|pack|pieces?|items?)',  # 2 pcs, 3 pack
        r'\((\d+)\)',  # (2) format
        r'qty[:\s]*(\d+)',  # qty: 2 format
        r'quantity[:\s]*(\d+)',  # quantity: 2 format
    ]

    qty = 1
    for pattern in qty_patterns:
        q_match = re.search(pattern, raw, re.IGNORECASE)
        if q_match:
            try:
                qty = int(q_match.group(1))
                break
            except:
                continue

    # Clean the item name
    name = clean_item_name(name_part)
    if not name or len(name) < 2:
        return None

    # Additional validation - skip if name is too short or looks like a code
    if len(name) < 2 or re.match(r'^[A-Z0-9]{1,3}$', name.upper()):
        return None

    return {
        'name': name,
        'qty': qty,
        'raw_line': raw,
        'price': price,
        'confidence': 'high' if qty > 1 else 'medium'
    }

def extract_items_from_image(image_bytes: bytes):
    """Enhanced item extraction with multiple OCR strategies."""
    items = []

    # Try multiple preprocessing and OCR configurations
    configurations = [
        {'preprocess': True, 'config': '--oem 3 --psm 6', 'lang': 'eng'},
        {'preprocess': True, 'config': '--oem 3 --psm 3', 'lang': 'eng'},  # Better for uniform text
        {'preprocess': False, 'config': '--oem 3 --psm 6', 'lang': 'eng'},  # No preprocessing
        {'preprocess': True, 'config': '--oem 1 --psm 6', 'lang': 'eng'},  # Neural nets OCR
    ]

    for config in configurations:
        try:
            if config['preprocess']:
                img = preprocess_image_bytes(image_bytes)
            else:
                img = Image.open(io.BytesIO(image_bytes)).convert('RGB')

            # Try structured text extraction first
            lines = _reconstruct_lines_enhanced(img, config['config'], config['lang'])
            for ln in lines:
                it = _parse_line(ln)
                if it and it['name'] not in [item['name'] for item in items]:
                    items.append(it)

            # If no items found with structured extraction, try full text extraction
            if not items:
                text = pytesseract.image_to_string(img, lang=config['lang'], config=config['config'])
                for line in text.splitlines():
                    it = _parse_line(line)
                    if it and it['name'] not in [item['name'] for item in items]:
                        items.append(it)

        except Exception as e:
            print(f"OCR configuration {config} failed: {e}")
            continue

    # Remove duplicates and sort by confidence
    unique_items = []
    seen_names = set()

    for item in items:
        name = item['name'].lower()
        if name not in seen_names:
            unique_items.append(item)
            seen_names.add(name)

    # Sort by confidence and price (higher price items first)
    unique_items.sort(key=lambda x: (x.get('confidence', 'low'), x.get('price', 0)), reverse=True)

    return unique_items[:20]  # Return top 20 items

def _reconstruct_lines_enhanced(img, config, lang):
    """Enhanced line reconstruction with better text grouping."""
    df = pytesseract.image_to_data(img, output_type=Output.DATAFRAME, config=config, lang=lang)
    df = df.dropna(subset=['text']).copy()
    df = df[df['conf'] > 30]  # Lower confidence threshold

    lines = []
    if df.empty:
        return lines

    # Group by line with better logic
    for key, group in df.groupby(['page_num','block_num','par_num','line_num']):
        g = group.sort_values('left')
        text = ' '.join(str(t) for t in g['text'].tolist()).strip()

        # Filter out very short or meaningless text
        if text and len(text) > 1 and not re.match(r'^[^\w]*$', text):
            lines.append(text)

    return lines
