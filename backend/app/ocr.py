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
    text = raw.lower().strip()
    
    # Common OCR typo corrections
    text = re.sub(r'mi1k', 'milk', text)
    text = re.sub(r'eggs?', 'eggs', text)
    text = re.sub(r'bread', 'bread', text)
    text = re.sub(r'chicken', 'chicken', text)
    text = re.sub(r'coffee', 'coffee', text)
    text = re.sub(r'beef', 'beef', text)
    text = re.sub(r'pork', 'pork', text)
    text = re.sub(r'fish', 'fish', text)
    text = re.sub(r'cheese', 'cheese', text)
    text = re.sub(r'rice', 'rice', text)
    text = re.sub(r'potatoes?', 'potatoes', text)
    text = re.sub(r'tomatoes?', 'tomatoes', text)
    
    # Remove prices like 2.99, $3.50
    text = re.sub(r"\d+(\.\d{1,2})?", "", text)
    # Remove symbols
    text = re.sub(r"[^a-z\s]", "", text)
    # Normalize spacing
    text = re.sub(r"\s+", " ", text).strip()
    
    # Skip if it's a total/subtotal keyword
    if text in ['total', 'subtotal', 'tax', 'vat', 'change', 'cash', 'card', 'balance', 'pay', 'amount', 'discount']:
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
    raw = line.strip()
    if not raw:
        return None
    up = re.sub(r'[^A-Z ]+', '', raw.upper())
    if any(k in up for k in IGNORE_KEYWORDS):
        return None
    m = PRICE_RE_END.search(raw)
    if not m:
        return None
    price_str = m.group(1).replace(',', '.')
    try:
        price = float(price_str)
    except:
        return None
    name = clean_item_name(raw[:m.start()].strip(' -:'))
    if not name or len(name) < 2:
        return None
    qty = 1
    q = QTY_X_RE.search(raw) or QTY_PCS_RE.search(raw)
    if q:
        try:
            qty = int(q.group(1))
        except:
            qty = 1
    return {'name': name, 'qty': qty, 'raw_line': raw, 'price': price}

def extract_items_from_image(image_bytes: bytes):
    img = preprocess_image_bytes(image_bytes)
    lines = _reconstruct_lines(img)
    items = []
    for ln in lines:
        it = _parse_line(ln)
        if it:
            items.append(it)
    if not items:
        cfg = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, lang='eng', config=cfg)
        for line in text.splitlines():
            it = _parse_line(line)
            if it:
                items.append(it)
    return items
