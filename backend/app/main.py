import os, json, sqlite3
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .ocr import extract_items_from_image
from .footprint import FootprintMatcher, load_dataset
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'receipts.db')
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'greenhouse-gas-emissions-per-kilogram-of-food-product.csv')

app = FastAPI(title='EcoBasket API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        total_footprint REAL,
        raw_json TEXT
    )""")
    conn.commit()
    conn.close()
init_db()

matcher = FootprintMatcher(load_dataset(DATASET_PATH))

@app.post('/upload_receipt')
async def upload_receipt(file: UploadFile = File(...), user_id: str = 'demo_user'):
    contents = await file.read()
    try:
        items = extract_items_from_image(contents)
        print(f"DEBUG: OCR extracted items: {items}")  # Debug output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'OCR failed: {e}')

    results, total = matcher.match_and_compute(items)
    print(f"DEBUG: Matching results: {results}")  # Debug output

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO receipts (user_id, date, total_footprint, raw_json) VALUES (?, ?, ?, ?)',
              (user_id, datetime.utcnow().isoformat(), float(total), json.dumps({'items': results})))
    conn.commit()
    conn.close()
    return {'items': results, 'total_footprint': total}

@app.get('/footprint_history')
def footprint_history(user_id: str = 'demo_user'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, date, total_footprint, raw_json FROM receipts WHERE user_id=? ORDER BY date DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({'id': r[0], 'date': r[1], 'total_footprint': r[2], 'data': json.loads(r[3])})
    return {'history': out}
