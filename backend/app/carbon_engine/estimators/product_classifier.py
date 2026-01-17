def classify_product(product_name):
    name = product_name.lower()

    if "jeans" in name or "denim" in name:
        return "apparel", 0.9

    if "shirt" in name or "top" in name:
        return "apparel", 0.6

    if "window" in name or "grill" in name or "gate" in name:
        return "metal_fabrication", 0.7

    if "steel" in name:
        return "metal_fabrication", 0.5

    return "unknown", 0.0
