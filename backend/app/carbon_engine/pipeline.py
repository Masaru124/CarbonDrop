import json
import os

from .estimators.product_classifier import classify_product
from .estimators.material_estimator import estimate_materials
from .estimators.process_estimator import estimate_processes

from .calculator.material_emission import calculate_material_emission
from .calculator.process_emission import calculate_process_emission
from .calculator.energy_emission import calculate_energy_emission
from .calculator.total_emission import calculate_total


# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# -------------------------------
# Clarification logic for vague products (non-interactive)
# -------------------------------
def clarify_product(product_name, product_type, confidence):
    """Auto-detect product details with defaults when confidence is low."""
    details = {}

    # Apparel clarification with defaults
    if product_type == "apparel":
        details["gender"] = "unisex"
        details["fabric"] = "cotton"

    # Metal fabrication clarification with defaults
    elif product_type == "metal_fabrication":
        details["usage"] = "indoor"
        details["thickness"] = "medium"

    # Unknown product with defaults
    else:
        details["material"] = "plastic"
        details["purpose"] = "general"

    return details


# -------------------------------
# Core pipeline
# -------------------------------
def run_pipeline(product_name, weight, energy_kwh, region="India"):
    product_type, confidence = classify_product(product_name)

    details = {}
    if confidence < 0.8:
        details = clarify_product(product_name, product_type, confidence)

    # Load datasets with correct paths
    data_dir = os.path.join(BASE_DIR, "data")
    
    raw_factors = {}
    process_factors = {}
    energy_factors = {}
    
    raw_json_path = os.path.join(data_dir, "raw.json")
    process_json_path = os.path.join(data_dir, "process.json")
    energy_json_path = os.path.join(data_dir, "region_energy.json")
    
    if os.path.exists(raw_json_path):
        with open(raw_json_path) as f:
            raw_factors = json.load(f)
    
    if os.path.exists(process_json_path):
        with open(process_json_path) as f:
            process_factors = json.load(f)
    
    if os.path.exists(energy_json_path):
        with open(energy_json_path) as f:
            energy_factors = json.load(f)

    # Estimate materials & processes
    materials = estimate_materials(product_type, weight, details)
    processes = estimate_processes(product_type)

    # Calculate emissions
    material_emission = calculate_material_emission(
        materials, raw_factors
    )

    process_emission = calculate_process_emission(
        processes, weight, process_factors
    )

    energy_emission = calculate_energy_emission(
        energy_kwh, energy_factors.get(region, {}).get("electricity", 0)
    )

    total_emission = calculate_total(
        material_emission,
        process_emission,
        energy_emission
    )

    return {
        "product": product_name,
        "category": product_type,
        "confidence": confidence,
        "materials": materials,
        "material_emission": round(material_emission, 2),
        "process_emission": round(process_emission, 2),
        "energy_emission": round(energy_emission, 2),
        "total_emission": round(total_emission, 2),
    }


# -------------------------------
# INTERACTIVE TERMINAL ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    print("\n===================================")
    print("  CARBON EMISSION ESTIMATION TOOL  ")
    print("===================================\n")

    product_name = input("Enter product name: ").strip()

    weight = 10  # Default weight
    energy_kwh = 0  # Default energy

    region = input(
        "Enter region (default: India): "
    ).strip() or "India"

    result = run_pipeline(
        product_name=product_name,
        weight=weight,
        energy_kwh=energy_kwh,
        region=region
    )

    output = {
        "product": result["product"],
        "category": result["category"],
        "confidence": round(result["confidence"], 2),
        "inputs": {
            "weight_kg": weight,
            "energy_kwh": energy_kwh,
            "region": region
        },
        "materials": result["materials"],
        "emissions_kg_co2": {
            "material": result["material_emission"],
            "process": result["process_emission"],
            "energy": result["energy_emission"],
            "total": result["total_emission"]
        }
    }

    print("\n===== JSON OUTPUT =====")
    print(json.dumps(output, indent=4))

