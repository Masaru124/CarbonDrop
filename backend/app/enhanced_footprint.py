from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import os
import sqlite3

from rapidfuzz import fuzz, process

from .carbon_engine.pipeline import run_pipeline
from .footprint import estimate_food_footprint, find_best_dataset_match, load_dataset, normalize_item_text

DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset"
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "carbondrop.db"


@dataclass(frozen=True)
class EmissionFactorRecord:
    id: str
    name: str
    category: str
    subcategory: str | None
    kg_co2e_per_unit: float
    unit: str
    confidence: str
    source: str | None
    source_url: str | None
    region: str
    notes: str | None


class EnhancedFootprintMatcher:
    """
    Unified footprint matcher that resolves emissions in this order:
    1. Normalized emission_factors table
    2. Food dataset match/fallback
    3. Raw material pipeline for remaining gaps
    """

    SIMPLE_CATEGORIES = {"utility", "transport", "energy", "apparel", "goods", "electronics", "household", "restaurant", "fuel"}
    FOOD_CATEGORY = "food"
    SHORT_VALID_TOKENS = {
        "tea", "egg", "eggs", "oil", "jam", "salt", "soup", "cola", "cola", "rum", "gin", "ice"
    }
    CATEGORY_KEYWORDS = {
        "food": {
            "lassi", "milk", "dairy", "yogurt", "curd", "paneer", "cheese", "butter", "cream",
            "biscuit", "biscuits", "cookie", "cookies", "noodle", "noodles", "instant noodles", "momo", "momos",
            "bread", "rice", "tea", "coffee", "juice", "snack", "chips", "cake", "chocolate", "sugar", "flour",
            "flavoured milk", "flavored milk", "milk drink", "shake", "lassi", "flavoured", "flavored"
        },
        "transport": {"taxi", "cab", "bus", "train", "flight", "fuel", "petrol", "diesel", "uber", "ola"},
        "utility": {"electricity", "water", "gas", "kwh", "meter", "bill"},
        "energy": {"charging", "charger", "battery", "power"},
        "household": {"soap", "shampoo", "detergent", "cleaner", "bag", "bottle", "container", "toy", "plush"},
        "apparel": {"shirt", "tshirt", "jeans", "dress", "shoe", "shoes", "pant", "cap"},
        "restaurant": {"meal", "biryani", "burger", "pizza", "sandwich", "restaurant"},
    }

    def __init__(self):
        self.food_df = load_dataset(DATASET_PATH)
        self.food_choices = list(self.food_df[self.food_df["category"].astype(str).str.lower() == self.FOOD_CATEGORY]["item"])
        self.emission_factors = self._load_emission_factors()
        self.factor_lookup = self._build_factor_lookup(self.emission_factors)

    def match_and_compute(self, items: List[dict]) -> Tuple[List[dict], float]:
        results = []
        total = 0.0

        for it in items:
            name = str(it.get("name", "")).strip()
            qty = float(it.get("qty", 1) or 1)
            unit = str(it.get("unit", "")).strip()
            category = str(it.get("category") or "unknown").lower()

            if not self._is_plausible_product_name(name):
                continue

            category = self._normalize_category(category, name)

            factor = self._match_factor(name=name, category=category, unit=unit)
            if factor is not None:
                footprint = round(qty * factor.kg_co2e_per_unit, 4)
                result = self._format_result(
                    name=name,
                    matched_name=factor.name,
                    match_score=self._confidence_to_score(factor.confidence),
                    qty=qty,
                    unit=unit,
                    footprint=footprint,
                    category=category,
                )
            elif category == self.FOOD_CATEGORY:
                best = find_best_dataset_match(self.food_df, name, requested_unit=unit, category=self.FOOD_CATEGORY)
                if best:
                    footprint = round(qty * float(best["co2_per_unit"]), 4)
                    result = self._format_result(
                        name=name,
                        matched_name=best["matched_name"],
                        match_score=int(best["match_score"]),
                        qty=qty,
                        unit=unit,
                        footprint=footprint,
                        category=category,
                    )
                else:
                    footprint, confidence, matched_name = estimate_food_footprint(self.food_df, name, qty)
                    if footprint <= 0:
                        food_median = self._food_dataset_median()
                        if food_median > 0:
                            footprint = round(qty * food_median, 4)
                            confidence = 0.45
                            matched_name = "estimated_from_food_average"
                        else:
                            footprint, confidence = self._compute_via_pipeline(name)
                            matched_name = "estimated_via_pipeline"
                    result = self._format_result(
                        name=name,
                        matched_name=matched_name,
                        match_score=int(confidence * 100) if confidence else 0,
                        qty=qty,
                        unit=unit,
                        footprint=footprint,
                        category=category,
                    )
            else:
                if category == "other":
                    food_best = find_best_dataset_match(self.food_df, name, requested_unit=unit, category=self.FOOD_CATEGORY)
                    if food_best:
                        footprint = round(qty * float(food_best["co2_per_unit"]), 4)
                        result = self._format_result(
                            name=name,
                            matched_name=food_best["matched_name"],
                            match_score=int(food_best["match_score"]),
                            qty=qty,
                            unit=unit,
                            footprint=footprint,
                            category=self.FOOD_CATEGORY,
                        )
                        results.append(result)
                        total += footprint
                        continue

                footprint, confidence = self._compute_via_pipeline(name)
                if footprint <= 0 and self._normalize_category(category, name) == self.FOOD_CATEGORY:
                    food_median = self._food_dataset_median()
                    if food_median > 0:
                        footprint = round(qty * food_median, 4)
                        confidence = max(confidence, 0.45)
                        result = self._format_result(
                            name=name,
                            matched_name="estimated_from_food_average",
                            match_score=int(confidence * 100) if confidence else 45,
                            qty=qty,
                            unit=unit,
                            footprint=footprint,
                            category=self.FOOD_CATEGORY,
                        )
                        results.append(result)
                        total += footprint
                        continue

                result = self._format_result(
                    name=name,
                    matched_name="estimated_via_pipeline",
                    match_score=int(confidence * 100) if confidence else 0,
                    qty=qty,
                    unit=unit,
                    footprint=footprint,
                    category=category,
                )

            results.append(result)
            total += footprint

        return results, round(total, 4)

    def _compute_via_pipeline(self, product_name: str) -> Tuple[float, float]:
        try:
            pipeline_result = run_pipeline(
                product_name=product_name,
                weight=1.0,
                energy_kwh=0,
                region="India",
            )
            return float(pipeline_result["total_emission"]), float(pipeline_result["confidence"])
        except Exception as exc:
            print(f"[Pipeline Error] {product_name}: {exc}")
            return 0.0, 0.0

    def _compute_simple(self, category: str, qty: float, unit: str, name: str) -> float:
        factor = self._match_factor(name=name, category=category, unit=unit)
        if factor is not None:
            return round(qty * factor.kg_co2e_per_unit, 4)
        return 0.0

    def _format_result(
        self,
        name: str,
        matched_name: str,
        match_score: int,
        qty: float,
        unit: str,
        footprint: float,
        category: str,
    ) -> dict:
        return {
            "name": name,
            "matched_name": matched_name,
            "match_score": match_score,
            "qty": qty,
            "unit": unit,
            "co2_per_unit": round(footprint / qty, 4) if qty > 0 else 0,
            "footprint": round(footprint, 4),
            "category": category,
        }

    def _resolve_sqlite_db_path(self) -> Path:
        database_url = os.environ.get("DATABASE_URL", "")
        if database_url.startswith("sqlite:///"):
            return Path(database_url.replace("sqlite:///", "", 1)).expanduser().resolve()
        return DEFAULT_DB_PATH.resolve()

    def _normalize_unit_text(self, value) -> str:
        if value is None:
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
            "item": "item",
            "items": "item",
            "piece": "item",
            "pieces": "item",
            "pcs": "item",
            "portion": "portion",
            "km": "km",
            "kwh": "kwh",
        }
        return aliases.get(text, text)

    def _normalize_factor_key(self, name: str, unit: str) -> str:
        normalized_name = normalize_item_text(name, strip_modifiers=True)
        normalized_unit = self._normalize_unit_text(unit)
        key = f"{normalized_name}.{normalized_unit}".strip(".")
        return key.lower()

    def _load_emission_factors(self) -> List[EmissionFactorRecord]:
        db_path = self._resolve_sqlite_db_path()
        if not db_path.exists():
            return []

        connection = None
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, name, category, subcategory, kg_co2e_per_unit, unit,
                       confidence, source, source_url, region, notes
                FROM emission_factors
                """
            ).fetchall()
        except Exception:
            return []
        finally:
            if connection is not None:
                connection.close()

        records: List[EmissionFactorRecord] = []
        for row in rows:
            try:
                records.append(
                    EmissionFactorRecord(
                        id=str(row["id"]),
                        name=str(row["name"]),
                        category=str(row["category"]),
                        subcategory=str(row["subcategory"]) if row["subcategory"] is not None else None,
                        kg_co2e_per_unit=float(row["kg_co2e_per_unit"]),
                        unit=str(row["unit"]),
                        confidence=str(row["confidence"]),
                        source=str(row["source"]) if row["source"] is not None else None,
                        source_url=str(row["source_url"]) if row["source_url"] is not None else None,
                        region=str(row["region"]),
                        notes=str(row["notes"]) if row["notes"] is not None else None,
                    )
                )
            except Exception:
                continue

        return records

    def _build_factor_lookup(self, factors: List[EmissionFactorRecord]) -> dict[str, EmissionFactorRecord]:
        lookup: dict[str, EmissionFactorRecord] = {}
        for factor in factors:
            lookup[factor.id.lower()] = factor
            lookup[self._normalize_factor_key(factor.name, factor.unit)] = factor
            if factor.subcategory:
                lookup[self._normalize_factor_key(factor.name, factor.subcategory)] = factor
            lookup[normalize_item_text(factor.name, strip_modifiers=True).lower()] = factor
        return lookup

    def _confidence_to_score(self, confidence: str) -> int:
        mapping = {"high": 95, "medium": 80, "low": 60}
        return mapping.get(str(confidence).lower(), 50)

    def _normalize_category(self, category: str, name: str) -> str:
        lowered_name = normalize_item_text(name, strip_modifiers=True)
        current = str(category or "unknown").lower().strip()
        if current and current != "other":
            return current

        for inferred_category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in lowered_name for keyword in keywords):
                return inferred_category

        return current or "other"

    def _food_dataset_median(self) -> float:
        try:
            food_values = self.food_df[self.food_df["category"].astype(str).str.lower() == self.FOOD_CATEGORY]["co2"]
            return float(food_values.dropna().median() or 0.0)
        except Exception:
            return 0.0

    def _is_plausible_product_name(self, name: str) -> bool:
        normalized = normalize_item_text(name, strip_modifiers=True)
        if not normalized:
            return False

        tokens = normalized.split()
        if not tokens:
            return False

        stopwords = {"a", "an", "and", "or", "on", "in", "of", "to", "x", "e", "s", "es", "at"}
        meaningful_tokens = [token for token in tokens if token not in stopwords]
        if len(meaningful_tokens) < 1:
            return False

        if len(meaningful_tokens) == 1:
            token = meaningful_tokens[0]
            if len(token) < 4 and token not in self.SHORT_VALID_TOKENS:
                return False

        if len(normalized.replace(" ", "")) < 4:
            return False

        if len(meaningful_tokens) > 1 and not any(len(token) >= 4 for token in meaningful_tokens):
            return False

        if len(meaningful_tokens) >= 2 and sum(len(token) <= 2 for token in meaningful_tokens) >= len(meaningful_tokens):
            return False

        return True

    def _match_factor(self, name: str, category: str, unit: str) -> EmissionFactorRecord | None:
        if not self.factor_lookup:
            return None

        normalized_name = normalize_item_text(name, strip_modifiers=True)
        normalized_unit = self._normalize_unit_text(unit)
        category = self._normalize_category(category, name)
        candidate_keys = [
            f"{category}.{normalized_name}.{normalized_unit}".strip(".").lower(),
            f"{category}.{normalized_name}".strip(".").lower(),
            f"{normalized_name}.{normalized_unit}".strip(".").lower(),
            normalized_name.lower(),
        ]

        for key in candidate_keys:
            factor = self.factor_lookup.get(key)
            if factor is not None:
                return factor

        factor_names = [
            factor.name
            for factor in self.emission_factors
            if factor.category.lower() == category.lower() or category.lower() in factor.id.lower()
        ]
        if not factor_names:
            factor_names = [factor.name for factor in self.emission_factors]

        best = process.extractOne(normalized_name, factor_names, scorer=fuzz.WRatio)
        if not best:
            return None

        matched_name, score, _ = best
        if score < 78:
            return None

        for factor in self.emission_factors:
            if factor.name == matched_name:
                return factor

        return None
