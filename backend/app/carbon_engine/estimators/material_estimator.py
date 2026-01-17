def estimate_materials(product_type, weight, details=None):
    details = details or {}

    if product_type == "apparel":
        fabric = details.get("fabric", "cotton")

        if fabric == "denim":
            return {"cotton": weight * 0.9, "dye": weight * 0.1}
        if fabric == "polyester":
            return {"plastic": weight}
        return {"cotton": weight}

    if product_type == "metal_fabrication":
        thickness = details.get("thickness", "medium")

        steel_ratio = {
            "thin": 0.8,
            "medium": 0.9,
            "thick": 0.95
        }.get(thickness, 0.9)

        return {"steel": weight * steel_ratio}

    return {"steel": weight}
