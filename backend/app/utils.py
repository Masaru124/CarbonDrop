import re

def normalize_quantity(text: str):
    """
    Converts raw text like '2kg rice', '1 packet milk', '500 g chicken'
    into (qty_kg, name).
    """
    text = text.lower()
    m = re.search(r"([\d.,]+)\s*(kg|g|packet|pack|ml|l)?", text)
    qty_kg = 1.0
    if m:
        num = float(m.group(1).replace(",", ""))
        unit = m.group(2) or ""
        if unit in ["kg"]:
            qty_kg = num
        elif unit in ["g"]:
            qty_kg = num / 1000
        elif unit in ["l"]:
            qty_kg = num  # assume 1L ~ 1kg
        elif unit in ["ml"]:
            qty_kg = num / 1000
        elif unit in ["packet", "pack"]:
            qty_kg = num * 0.5  # assume avg packet = 0.5kg
    return qty_kg, text
