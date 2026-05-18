from collections import defaultdict
from pathlib import Path
import os
import re

import pandas as pd
from rapidfuzz import fuzz, process


DATASET_CACHE_NAME = "merged_emissions_cache.csv"
DEFAULT_CATEGORY = "food"

ITEM_MODIFIERS = {
    "local",
    "organic",
    "fresh",
    "imported",
    "regional",
    "seasonal",
    "plain",
    "unsalted",
    "unsweetened",
    "lowfat",
    "fatfree",
    "b",
}

FOOD_GROUP_KEYWORDS = {
    "eggs": {"egg", "eggs"},
    "plant_milk": {"soy", "almond", "rice", "coconut", "pea"},
    "dairy": {"milk", "cheese", "yogurt", "cream", "butter"},
    "protein": {"beef", "lamb", "pork", "chicken", "turkey", "fish", "shrimp", "eggs", "egg", "tuna", "salmon", "bacon", "sausage"},
    "legumes": {"lentil", "lentils", "bean", "beans", "chickpea", "chickpeas", "peas", "pea", "tofu", "tempeh", "soy"},
    "grains": {"rice", "oat", "oats", "bread", "pasta", "noodle", "noodles", "cereal", "flour", "barley", "wheat", "quinoa"},
    "fruit": {"apple", "apples", "banana", "bananas", "orange", "oranges", "berry", "berries", "strawberry", "strawberries", "pear", "pears", "mango", "pineapple"},
    "vegetables": {"tomato", "tomatoes", "carrot", "carrots", "potato", "potatoes", "broccoli", "lettuce", "cucumber", "onion", "garlic", "spinach", "pepper", "cabbage"},
    "beverages": {"coffee", "tea", "juice", "water", "soda", "beer", "wine"},
}

TRUSTED_CATEGORIES = {
    "food",
    "transport",
    "utility",
    "energy",
    "water",
    "waste",
    "apparel",
    "material",
    "metal_fabrication",
    "restaurant",
    "invoice",
    "grocery",
    "unknown",
}


def _singularize_token(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("oes"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def normalize_item_text(value, strip_modifiers: bool = False) -> str:
    """Normalize item labels so receipt text and dataset text line up."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""

    text = str(value).lower().strip()
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return ""

    tokens = []
    for token in text.split():
        if strip_modifiers and token in ITEM_MODIFIERS:
            continue
        if strip_modifiers and len(token) == 1:
            continue
        token = _singularize_token(token) if strip_modifiers else token
        if token:
            tokens.append(token)

    return " ".join(tokens).strip()


def _normalize_unit_text(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""

    text = str(value).lower().strip()
    aliases = {
        "kilogram": "kg",
        "kilograms": "kg",
        "kgs": "kg",
        "gram": "g",
        "grams": "g",
        "liter": "l",
        "liters": "l",
        "litre": "l",
        "litres": "l",
        "milliliter": "ml",
        "milliliters": "ml",
        "millilitre": "ml",
        "millilitres": "ml",
        "piece": "pcs",
        "pieces": "pcs",
        "packet": "pack",
        "packets": "pack",
    }
    return aliases.get(text, text)


def _infer_default_category_from_path(csv_path: str) -> str:
    stem = Path(csv_path).stem.lower()
    if any(keyword in stem for keyword in ("transport", "travel")):
        return "transport"
    if any(keyword in stem for keyword in ("utility", "energy")):
        return "utility"
    return DEFAULT_CATEGORY


def _infer_food_group(text: str) -> str:
    tokens = set(normalize_item_text(text, strip_modifiers=True).split())
    if not tokens:
        return "other"

    if {"milk"} & tokens and tokens & FOOD_GROUP_KEYWORDS["plant_milk"]:
        return "plant_milk"

    for group_name, keywords in FOOD_GROUP_KEYWORDS.items():
        if tokens & keywords:
            return group_name

    return "other"


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lookup = {column.lower(): column for column in df.columns}
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    return None


def _score_text_column(series: pd.Series) -> float:
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]
    if values.empty:
        return -1.0

    total = len(values)
    alphabetic = sum(bool(re.search(r"[A-Za-z]", value)) for value in values)
    numeric_only = sum(bool(re.fullmatch(r"[\d.,/\-]+", value)) for value in values)
    comma_rich = sum("," in value for value in values)
    avg_length = sum(len(value) for value in values) / total

    return (
        (alphabetic / total) * 2.5
        + min(avg_length / 25.0, 1.0)
        + (comma_rich / total) * 0.5
        - (numeric_only / total) * 2.0
    )


def _select_item_column(df: pd.DataFrame) -> str | None:
    candidate_order = ["item", "product_name", "description", "name", "entity", "food", "category"]
    candidates: list[tuple[float, str]] = []

    lookup = {column.lower(): column for column in df.columns}
    for candidate in candidate_order:
        actual_column = lookup.get(candidate)
        if actual_column is None:
            continue
        score = _score_text_column(df[actual_column])
        if score > 0:
            candidates.append((score, actual_column))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def _category_column_is_trusted(series: pd.Series) -> bool:
    values = {
        normalize_item_text(value, strip_modifiers=True).replace(" ", "_")
        for value in series.dropna().tolist()
        if normalize_item_text(value, strip_modifiers=True)
    }

    if not values:
        return False

    return values.issubset(TRUSTED_CATEGORIES)


def _standardize_dataset_frame(df: pd.DataFrame, csv_path: str) -> pd.DataFrame | None:
    emission_column = _pick_column(df, ["co2", "emissions_per_kg", "emission", "carbon_footprint_per_kg", "carbon_footprint_per_100g"])
    if emission_column is None:
        return None

    item_column = _select_item_column(df)
    if item_column is None:
        item_column = next((column for column in df.columns if df[column].dtype == "object"), None)
    if item_column is None:
        return None

    unit_column = _pick_column(df, ["unit"])
    category_column = _pick_column(df, ["category"])
    source_column = _pick_column(df, ["source"])

    trusted_category = category_column if category_column and _category_column_is_trusted(df[category_column]) else None

    standardized = pd.DataFrame(
        {
            "item": df[item_column],
            "co2": pd.to_numeric(df[emission_column], errors="coerce"),
            "unit": df[unit_column] if unit_column else "kg",
            "category": df[trusted_category] if trusted_category else _infer_default_category_from_path(csv_path),
            "source": df[source_column] if source_column else Path(csv_path).stem,
        }
    )

    standardized["item"] = standardized["item"].astype(str).str.strip()
    standardized["unit"] = standardized["unit"].fillna("kg").astype(str).str.strip().str.lower()
    standardized["category"] = standardized["category"].fillna(_infer_default_category_from_path(csv_path)).astype(str).str.strip().str.lower()
    standardized["source"] = standardized["source"].fillna(Path(csv_path).stem).astype(str).str.strip()
    standardized = standardized.dropna(subset=["co2"])
    standardized = standardized[standardized["co2"] > 0]
    standardized = standardized[standardized["item"].str.len() > 0]

    standardized["item_key"] = standardized["item"].map(normalize_item_text)
    standardized["match_key"] = standardized["item"].map(lambda value: normalize_item_text(value, strip_modifiers=True))
    standardized["match_tokens"] = standardized["match_key"].map(lambda value: tuple(value.split()))
    standardized = standardized[standardized["item_key"].str.len() > 0]

    return standardized


def _combine_dataset_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    combined = pd.concat(frames, ignore_index=True)

    def _join_unique(values) -> str:
        seen = []
        for value in values:
            text = str(value).strip()
            if text and text not in seen:
                seen.append(text)
        return "; ".join(seen)

    aggregated = (
        combined.groupby(["item_key", "unit", "category"], as_index=False)
        .agg(
            {
                "item": "first",
                "co2": "median",
                "source": _join_unique,
                "match_key": "first",
                "match_tokens": "first",
            }
        )
    )

    aggregated = aggregated.sort_values(["category", "item_key", "unit"]).reset_index(drop=True)
    aggregated["co2"] = pd.to_numeric(aggregated["co2"], errors="coerce")
    aggregated = aggregated.dropna(subset=["co2"])
    aggregated = aggregated[aggregated["co2"] > 0]
    return aggregated


def _unit_score(candidate_unit: str, requested_unit: str) -> float:
    candidate = _normalize_unit_text(candidate_unit)
    requested = _normalize_unit_text(requested_unit)

    if not requested or not candidate:
        return 0.5

    if candidate == requested:
        return 1.0

    compatible_pairs = {
        ("kg", "l"),
        ("l", "kg"),
        ("g", "kg"),
        ("kg", "g"),
    }
    if (candidate, requested) in compatible_pairs:
        return 0.75

    return 0.0


def find_best_dataset_match(dataset_df: pd.DataFrame, item_name: str, requested_unit: str = "", category: str | None = None):
    """Find the best exact or fuzzy match in the merged dataset."""
    if dataset_df.empty:
        return None

    query_key = normalize_item_text(item_name, strip_modifiers=True)
    if not query_key:
        return None

    pool = dataset_df
    if category:
        pool = pool[pool["category"].astype(str).str.lower() == category.lower()]

    if pool.empty:
        return None

    exact_matches = pool[pool["match_key"] == query_key]
    if not exact_matches.empty:
        exact_matches = exact_matches.copy()
        exact_matches["unit_score"] = exact_matches["unit"].map(lambda value: _unit_score(value, requested_unit))
        exact_matches["final_score"] = exact_matches["unit_score"].map(lambda score: 95 + int(score * 5))
        best_exact = exact_matches.sort_values(["unit_score", "co2"], ascending=[False, False]).iloc[0]
        if requested_unit and float(best_exact["unit_score"]) <= 0:
            return None
        return {
            "name": item_name,
            "matched_name": best_exact["item"],
            "match_score": int(best_exact["final_score"]),
            "co2_per_unit": float(best_exact["co2"]),
            "unit": best_exact["unit"],
            "category": best_exact["category"],
            "source": best_exact["source"],
        }

    query_tokens = set(query_key.split())
    if query_tokens:
        token_pool = pool[pool["match_tokens"].map(lambda tokens: bool(query_tokens & set(tokens)))].copy()
        if not token_pool.empty:
            pool = token_pool

    if pool.empty:
        return None

    unique_candidates = pool.drop_duplicates(subset=["match_key", "unit", "category"])
    if unique_candidates.empty:
        return None

    candidate_keys = unique_candidates["match_key"].tolist()
    scorer = fuzz.WRatio if len(query_tokens) > 1 else fuzz.ratio
    best = process.extractOne(query_key, candidate_keys, scorer=scorer)
    if not best:
        return None

    matched_key, text_score, _ = best
    candidate_rows = unique_candidates[unique_candidates["match_key"] == matched_key].copy()
    if candidate_rows.empty:
        return None

    candidate_rows["unit_score"] = candidate_rows["unit"].map(lambda value: _unit_score(value, requested_unit))
    candidate_rows["final_score"] = candidate_rows["unit_score"].map(lambda score: int(round(text_score * 0.9 + score * 10)))
    best_row = candidate_rows.sort_values(["final_score", "unit_score", "co2"], ascending=[False, False, False]).iloc[0]

    token_count = max(1, len(query_tokens))
    threshold = 88 if token_count <= 2 else 80
    candidate_token_count = len(str(best_row["match_key"]).split())
    if token_count <= 2 and candidate_token_count > token_count + 1 and text_score < 95:
        return None
    if int(best_row["final_score"]) < threshold:
        return None

    return {
        "name": item_name,
        "matched_name": best_row["item"],
        "match_score": int(best_row["final_score"]),
        "co2_per_unit": float(best_row["co2"]),
        "unit": best_row["unit"],
        "category": best_row["category"],
        "source": best_row["source"],
    }


def estimate_food_footprint(dataset_df: pd.DataFrame, item_name: str, qty: float) -> tuple[float, float, str]:
    """Estimate emissions for an unseen food item using dataset-derived formulae."""
    food_df = dataset_df[dataset_df["category"].astype(str).str.lower() == "food"].copy()
    if food_df.empty:
        return 0.0, 0.0, "predicted_food_average"

    food_df["group"] = food_df["match_key"].map(_infer_food_group)
    overall_median = float(pd.to_numeric(food_df["co2"], errors="coerce").dropna().median())
    if overall_median <= 0:
        overall_median = float(pd.to_numeric(dataset_df["co2"], errors="coerce").dropna().median() or 0.0)

    if overall_median <= 0:
        return 0.0, 0.0, "predicted_food_average"

    group = _infer_food_group(item_name)
    group_values = pd.to_numeric(food_df.loc[food_df["group"] == group, "co2"], errors="coerce").dropna()
    if not group_values.empty:
        co2_per_unit = float(group_values.median())
        confidence = 0.68 if group != "other" else 0.58
        matched_name = f"predicted_from_{group}_average"
    else:
        co2_per_unit = overall_median
        confidence = 0.5
        matched_name = "predicted_from_food_average"

    footprint = round(qty * co2_per_unit, 4)
    return footprint, confidence, matched_name

class FootprintMatcher:
    def __init__(self, dataset_df):
        self.df = dataset_df.copy()
        if "match_key" not in self.df.columns:
            self.df["match_key"] = self.df["item"].map(normalize_item_text)
        if "match_tokens" not in self.df.columns:
            self.df["match_tokens"] = self.df["match_key"].map(lambda value: tuple(value.split()))
        if "unit" not in self.df.columns:
            self.df["unit"] = "kg"
        if "category" not in self.df.columns:
            self.df["category"] = DEFAULT_CATEGORY
        self.choices = list(self.df['item'])

    def match_and_compute(self, items):
        results = []
        total = 0.0
        for it in items:
            name = it.get('name', '').strip()
            qty = float(it.get('qty', 1) or 1)
            match = find_best_dataset_match(self.df, name, requested_unit=it.get('unit', ''))
            if match:
                footprint = round(qty * float(match['co2_per_unit']), 4)
                results.append({'name': name, 'matched_name': match['matched_name'], 'match_score': int(match['match_score']),
                                'qty': qty, 'unit': match['unit'], 'co2_per_unit': float(match['co2_per_unit']),
                                'footprint': footprint, 'category': match['category']})
                total += footprint
            else:
                results.append({'name': name, 'matched_name': None, 'match_score': 0,
                                'qty': qty, 'unit': None, 'co2_per_unit': None,
                                'footprint': 0.0})
        return results, round(total, 4)

def load_dataset(csv_path):
    """Load and merge every emissions CSV in the dataset folder."""
    dataset_path = Path(csv_path)
    dataset_dir = dataset_path if dataset_path.is_dir() else dataset_path.parent
    dataset_dir = dataset_dir.resolve()

    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    cache_path = dataset_dir / DATASET_CACHE_NAME
    csv_files = [path for path in sorted(dataset_dir.glob("*.csv")) if path.name != DATASET_CACHE_NAME]

    frames = []
    for csv_file in csv_files:
        try:
            raw_df = pd.read_csv(csv_file)
        except Exception as exc:
            print(f"Skipping {csv_file.name}: {exc}")
            continue

        standardized = _standardize_dataset_frame(raw_df, str(csv_file))
        if standardized is None or standardized.empty:
            continue

        frames.append(standardized)

    if not frames:
        raise FileNotFoundError(f"No emissions datasets could be loaded from {dataset_dir}")

    combined = _combine_dataset_frames(frames)

    try:
        combined.to_csv(cache_path, index=False)
        print(f"Merged dataset cached at {cache_path}")
    except Exception as exc:
        print(f"Could not write cache file {cache_path}: {exc}")

    print(f"Loaded {len(csv_files)} CSV files from {dataset_dir}")
    print(f"Merged dataset shape: {combined.shape}")
    return combined

class WhatIfSimulator:
    def __init__(self, dataset_df):
        self.df = dataset_df.copy()

        # Enhanced transport emission factors from DEFRA
        self.transport_factors = {
            'flight': 0.25,  # kg CO2e per km for short flights (average)
            'train': 0.04,   # kg CO2e per km for train (average)
            'bus': 0.08,     # kg CO2e per km for bus
            'car': 0.17,     # kg CO2e per km for average car
            'taxi': 0.17,    # kg CO2e per km for taxi
            'electric_car': 0.054,  # kg CO2e per km for electric car
        }

        # Enhanced energy factors from DEFRA
        self.energy_factors = {
            'electricity': 0.207,  # kg CO2e per kWh
            'natural_gas': 0.184,  # kg CO2e per kWh
            'gas': 0.184,          # kg CO2e per kWh
            'fuel_oil': 0.246,     # kg CO2e per kWh
            'lpg': 0.215,          # kg CO2e per kWh
            'coal': 0.345,         # kg CO2e per kWh
        }

        # Water factors
        self.water_factors = {
            'water': 0.0013,  # kg CO2e per liter (supply + treatment)
        }

    def _get_emission_factor(self, item_name, category='food'):
        """Get emission factor from the dataset."""
        # Look for exact match first
        matches = self.df[(self.df['item'].str.lower() == item_name.lower()) &
                         (self.df['category'] == category)]

        if not matches.empty:
            return float(matches.iloc[0]['co2'])

        # Look for partial matches
        matches = self.df[self.df['item'].str.lower().str.contains(item_name.lower()) &
                         (self.df['category'] == category)]

        if not matches.empty:
            return float(matches.iloc[0]['co2'])

        return None

    def simulate_meat_replacement(self, meat_meals_per_week, weeks=52):
        """
        Simulate replacing meat meals with plant-based alternatives.
        Assumes average meat meal is 200g beef, replaced with 200g lentils.
        """
        # Get CO2 for beef (meat)
        beef_co2 = self._get_emission_factor('beef', 'food')
        if beef_co2 is None:
            beef_co2 = 27.0  # Default value from dataset

        # Get CO2 for plant-based alternative (lentils)
        lentils_co2 = self._get_emission_factor('lentils', 'food')
        if lentils_co2 is None:
            lentils_co2 = 0.9  # Default value for lentils

        # Calculate weekly savings
        meat_per_meal = 0.2  # kg
        weekly_meat_co2 = meat_meals_per_week * meat_per_meal * beef_co2
        weekly_plant_co2 = meat_meals_per_week * meat_per_meal * lentils_co2
        weekly_savings = weekly_meat_co2 - weekly_plant_co2

        # Annual savings
        annual_savings = weekly_savings * weeks

        return {
            'scenario': f'Replace {meat_meals_per_week} meat meals/week with plant-based',
            'weekly_savings': round(weekly_savings, 2),
            'annual_savings': round(annual_savings, 2),
            'meat_co2_per_week': round(weekly_meat_co2, 2),
            'plant_co2_per_week': round(weekly_plant_co2, 2)
        }

    def simulate_transport_switch(self, trips_per_year, distance_per_trip_km, from_mode='flight', to_mode='train'):
        """
        Simulate switching from one transport mode to another for short trips.
        """
        if from_mode not in self.transport_factors or to_mode not in self.transport_factors:
            raise ValueError(f'Unsupported transport mode. Available: {list(self.transport_factors.keys())}')

        from_co2_per_km = self.transport_factors[from_mode]
        to_co2_per_km = self.transport_factors[to_mode]

        # Calculate annual emissions
        original_annual_co2 = trips_per_year * distance_per_trip_km * from_co2_per_km
        new_annual_co2 = trips_per_year * distance_per_trip_km * to_co2_per_km
        annual_savings = original_annual_co2 - new_annual_co2

        return {
            'scenario': f'Switch from {from_mode} to {to_mode} for {trips_per_year} trips/year ({distance_per_trip_km}km each)',
            'annual_savings': round(annual_savings, 2),
            'original_annual_co2': round(original_annual_co2, 2),
            'new_annual_co2': round(new_annual_co2, 2)
        }

    def simulate_energy_efficiency(self, current_bulbs, led_bulbs, hours_per_day=4, days_per_year=365):
        """
        Simulate switching from incandescent to LED bulbs.
        """
        # Energy consumption in kWh per year
        incandescent_wattage = 60  # watts per bulb
        led_wattage = 9  # watts per bulb
        kwh_per_watt_hour = 0.001  # conversion factor

        current_annual_kwh = current_bulbs * incandescent_wattage * hours_per_day * days_per_year * kwh_per_watt_hour
        new_annual_kwh = led_bulbs * led_wattage * hours_per_day * days_per_year * kwh_per_watt_hour
        annual_savings_kwh = current_annual_kwh - new_annual_kwh

        # CO2 emissions: ~0.4 kg CO2 per kWh (average grid mix)
        co2_per_kwh = 0.4
        annual_co2_savings = annual_savings_kwh * co2_per_kwh

        return {
            'scenario': f'Switch {current_bulbs} incandescent bulbs to {led_bulbs} LED bulbs',
            'annual_energy_savings': round(annual_savings_kwh, 2),
            'annual_co2_savings': round(annual_co2_savings, 2),
            'current_annual_kwh': round(current_annual_kwh, 2),
            'new_annual_kwh': round(new_annual_kwh, 2)
        }

    def simulate_electric_vehicle(self, annual_km, current_fuel_efficiency=10, ev_efficiency=0.2):
        """
        Simulate switching from gasoline car to electric vehicle.
        """
        # Fuel efficiency: L/100km for gas car, kWh/km for EV
        # CO2 emissions: ~2.3 kg CO2 per liter of gasoline
        co2_per_liter_gas = 2.3

        # Calculate annual fuel consumption and emissions
        current_fuel_liters = (annual_km / 100) * current_fuel_efficiency
        current_annual_co2 = current_fuel_liters * co2_per_liter_gas

        # EV energy consumption and emissions (assuming grid electricity)
        new_annual_kwh = annual_km * ev_efficiency
        new_annual_co2 = new_annual_kwh * 0.4  # kg CO2 per kWh
        annual_co2_savings = current_annual_co2 - new_annual_co2

        return {
            'scenario': f'Switch to electric vehicle for {annual_km} km/year',
            'annual_co2_savings': round(annual_co2_savings, 2),
            'current_annual_co2': round(current_annual_co2, 2),
            'new_annual_co2': round(new_annual_co2, 2),
            'current_fuel_liters': round(current_fuel_liters, 2),
            'new_annual_kwh': round(new_annual_kwh, 2)
        }

    def simulate_local_food(self, imported_meals_per_week, local_reduction_percent=50, weeks=52):
        """
        Simulate choosing local/seasonal food over imported food.
        """
        # Average CO2 impact: imported food travels ~2500km vs local food ~100km
        # Transport CO2: ~0.1 kg CO2 per ton-km
        imported_distance = 2500  # km
        local_distance = 100  # km

        # Assume average meal has 0.5kg of food transported
        food_per_meal = 0.5  # kg
        meals_reduced = imported_meals_per_week * (local_reduction_percent / 100)

        current_weekly_co2 = (imported_meals_per_week * food_per_meal * imported_distance * 0.1) / 1000
        new_weekly_co2 = (meals_reduced * food_per_meal * local_distance * 0.1) / 1000
        weekly_savings = current_weekly_co2 - new_weekly_co2
        annual_savings = weekly_savings * weeks

        return {
            'scenario': f'Reduce imported food by {local_reduction_percent}% ({imported_meals_per_week} meals/week)',
            'weekly_co2_savings': round(weekly_savings, 2),
            'annual_co2_savings': round(annual_savings, 2),
            'current_weekly_co2': round(current_weekly_co2, 2),
            'new_weekly_co2': round(new_weekly_co2, 2)
        }

    def simulate_waste_reduction(self, current_waste_kg_per_week, reduction_percent=30, weeks=52):
        """
        Simulate reducing food waste.
        """
        # CO2 impact of food waste: ~3.5 kg CO2 per kg of food waste
        co2_per_kg_waste = 3.5

        current_annual_waste = current_waste_kg_per_week * weeks
        reduced_waste = current_waste_kg_per_week * (reduction_percent / 100)
        new_annual_waste = current_annual_waste - reduced_waste * weeks

        current_annual_co2 = current_annual_waste * co2_per_kg_waste
        new_annual_co2 = new_annual_waste * co2_per_kg_waste
        annual_co2_savings = current_annual_co2 - new_annual_co2

        return {
            'scenario': f'Reduce food waste by {reduction_percent}% ({current_waste_kg_per_week} kg/week)',
            'annual_waste_reduction': round(reduced_waste * weeks, 2),
            'annual_co2_savings': round(annual_co2_savings, 2),
            'current_annual_co2': round(current_annual_co2, 2),
            'new_annual_co2': round(new_annual_co2, 2)
        }

# Offset conversion constants
CO2_PER_TREE_PER_YEAR = 21  # kg CO2 absorbed per tree per year
TREES_PER_OFFSET_CREDIT = 1000 / CO2_PER_TREE_PER_YEAR  # ~47.6 trees per 1000kg CO2

def calculate_trees_needed(co2_amount_kg):
    """
    Calculate number of trees needed to offset a given CO2 amount.
    """
    return max(1, round(co2_amount_kg / CO2_PER_TREE_PER_YEAR))

def calculate_offset_from_trees(trees_count):
    """
    Calculate CO2 offset from a given number of trees.
    """
    return round(trees_count * CO2_PER_TREE_PER_YEAR, 2)

def get_gamification_badge(total_trees):
    """
    Return gamification badge based on total trees planted.
    """
    if total_trees >= 500:
        return {"badge": "🌳 Forest Guardian", "level": "Expert"}
    elif total_trees >= 100:
        return {"badge": "🌲 Tree Champion", "level": "Advanced"}
    elif total_trees >= 25:
        return {"badge": "🌿 Nature Protector", "level": "Intermediate"}
    elif total_trees >= 5:
        return {"badge": "🌱 Seedling Planter", "level": "Beginner"}
    else:
        return {"badge": "🌰 Future Planter", "level": "Starter"}

def calculate_eco_credits(carbon_footprint_kg):
    """
    Calculate EcoCredits earned based on carbon footprint analysis.
    Lower footprint = more credits (rewarding sustainable choices).
    """
    # Base credits for uploading receipt
    base_credits = 10

    # Bonus credits based on footprint (lower footprint = more credits)
    if carbon_footprint_kg <= 10:
        footprint_bonus = 50  # Very low footprint
    elif carbon_footprint_kg <= 25:
        footprint_bonus = 30  # Low footprint
    elif carbon_footprint_kg <= 50:
        footprint_bonus = 20  # Moderate footprint
    elif carbon_footprint_kg <= 100:
        footprint_bonus = 10  # High footprint
    else:
        footprint_bonus = 5   # Very high footprint

    return base_credits + footprint_bonus

def get_credits_needed_for_tree():
    """
    Returns the number of EcoCredits needed to plant one tree.
    """
    return 100  # 100 credits = 1 tree
