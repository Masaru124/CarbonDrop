def estimate_processes(product_type):
    if product_type == "metal_fabrication":
        return ["cutting", "welding", "assembly"]

    if product_type == "furniture":
        return ["cutting", "assembly"]

    return ["assembly"]
