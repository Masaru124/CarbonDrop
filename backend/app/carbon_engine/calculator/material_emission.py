def calculate_material_emission(materials, factors):
    return sum(
        qty * factors.get(material, 0)
        for material, qty in materials.items()
    )
