from __future__ import annotations

import argparse
import csv
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DATASET_DIR = ROOT_DIR / "dataset"
DEFAULT_REGION = "global"
DEFAULT_DB_PATH = ROOT_DIR.parent / "carbondrop.db"


@dataclass(frozen=True)
class SeedRecord:
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


def _safe_text(value, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _normalize_item_text(value: str) -> str:
    text = _safe_text(value).lower().strip()
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _slug(text: str) -> str:
    normalized = _normalize_item_text(text)
    normalized = " ".join(normalized.split())
    return normalized.replace(" ", "_") or "factor"


def _normalize_unit(value: str | None) -> str:
    unit = _safe_text(value, "kg").lower()
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
    }
    return aliases.get(unit, unit)


def _pick_column(headers: Iterable[str], candidates: Iterable[str]) -> str | None:
    lookup = {header.lower(): header for header in headers}
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    return None


def _infer_category(headers: Iterable[str], dataset_name: str) -> str:
    lowered = {header.lower() for header in headers}
    if {"transport", "mode", "vehicle"} & lowered:
        return "transport"
    if {"utility", "energy", "electricity"} & lowered:
        return "utility"
    if {"apparel", "clothing", "garment"} & lowered:
        return "apparel"
    if "food" in dataset_name.lower() or "agribalyse" in dataset_name.lower():
        return "food"
    return "goods"


def _parse_confidence(raw_dqr: str | None) -> str:
    if raw_dqr is None:
        return "medium"

    try:
        score = float(str(raw_dqr).strip())
    except (TypeError, ValueError):
        return "medium"

    if score <= 1.5:
        return "high"
    if score <= 3.0:
        return "medium"
    return "low"


def _read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        return headers, list(reader)


def _parse_records_from_csv(csv_path: Path) -> list[SeedRecord]:
    headers, rows = _read_csv_rows(csv_path)
    if not headers or not rows:
        return []

    item_column = _pick_column(headers, ["item", "product", "product_name", "name", "description", "food"])
    emission_column = _pick_column(headers, ["co2", "co2e", "emissions", "emission", "kg_co2e", "kg_co2e_per_unit", "carbon_footprint"])
    unit_column = _pick_column(headers, ["unit", "units"])
    category_column = _pick_column(headers, ["category", "sector", "group"])
    subcategory_column = _pick_column(headers, ["subcategory", "sub_category", "type", "class"])
    source_column = _pick_column(headers, ["source", "dataset", "origin"])
    source_url_column = _pick_column(headers, ["source_url", "url", "reference_url"])
    region_column = _pick_column(headers, ["region", "locale", "country"])
    notes_column = _pick_column(headers, ["notes", "note", "comment", "comments"])
    dqr_column = _pick_column(headers, ["dqr", "data_quality", "quality", "uncertainty"])

    if item_column is None or emission_column is None:
        return []

    default_category = _infer_category(headers, csv_path.stem)
    records: list[SeedRecord] = []

    for row in rows:
        raw_name = _safe_text(row.get(item_column))
        raw_emission = _safe_text(row.get(emission_column))
        if not raw_name or not raw_emission:
            continue

        try:
            kg_co2e_per_unit = float(raw_emission)
        except (TypeError, ValueError):
            continue

        if kg_co2e_per_unit <= 0:
            continue

        category = _safe_text(row.get(category_column), default_category).lower() if category_column else default_category
        subcategory = _safe_text(row.get(subcategory_column)) if subcategory_column else ""
        unit = _normalize_unit(row.get(unit_column) if unit_column else "kg")
        source = _safe_text(row.get(source_column), csv_path.stem) if source_column else csv_path.stem
        source_url = _safe_text(row.get(source_url_column)) if source_url_column else ""
        region = _safe_text(row.get(region_column), DEFAULT_REGION).lower() if region_column else DEFAULT_REGION
        notes = _safe_text(row.get(notes_column)) if notes_column else ""
        confidence = _parse_confidence(row.get(dqr_column) if dqr_column else None)

        factor_id = ".".join(
            part
            for part in [
                _slug(category),
                _slug(subcategory) if subcategory else _slug(raw_name),
                _slug(raw_name),
            ]
            if part
        )

        records.append(
            SeedRecord(
                id=factor_id,
                name=raw_name,
                category=category,
                subcategory=subcategory or None,
                kg_co2e_per_unit=kg_co2e_per_unit,
                unit=unit,
                confidence=confidence,
                source=source or None,
                source_url=source_url or None,
                region=region or DEFAULT_REGION,
                notes=notes or None,
            )
        )

    return records


def _iter_dataset_files(dataset_dir: Path) -> list[Path]:
    preferred_names = [
        "agribalyse",
        "food",
        "transport",
        "defra",
        "energy",
        "apparel",
        "goods",
        "comprehensive_emissions",
        "combined_food_emissions",
        "defra_enhanced_emissions",
    ]
    csv_files = sorted(dataset_dir.glob("*.csv"))
    csv_files.sort(key=lambda path: (0 if any(name in path.stem.lower() for name in preferred_names) else 1, path.name.lower()))
    return csv_files


def _resolve_db_path() -> Path:
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url.startswith("sqlite:///"):
        return Path(database_url.replace("sqlite:///", "", 1)).expanduser().resolve()
    return DEFAULT_DB_PATH.resolve()


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS emission_factors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            kg_co2e_per_unit REAL NOT NULL,
            unit TEXT NOT NULL,
            confidence TEXT NOT NULL,
            source TEXT,
            source_url TEXT,
            region TEXT DEFAULT 'global',
            notes TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_emission_factors_category ON emission_factors(category)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_emission_factors_unit ON emission_factors(unit)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_emission_factors_region ON emission_factors(region)")


def seed_database(dataset_dir: Path) -> int:
    db_path = _resolve_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    upserts = 0

    try:
        _create_schema(connection)
        for csv_path in _iter_dataset_files(dataset_dir):
            records = _parse_records_from_csv(csv_path)
            for record in records:
                connection.execute(
                    """
                    INSERT INTO emission_factors (
                        id, name, category, subcategory, kg_co2e_per_unit,
                        unit, confidence, source, source_url, region, notes, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        category=excluded.category,
                        subcategory=excluded.subcategory,
                        kg_co2e_per_unit=excluded.kg_co2e_per_unit,
                        unit=excluded.unit,
                        confidence=excluded.confidence,
                        source=excluded.source,
                        source_url=excluded.source_url,
                        region=excluded.region,
                        notes=excluded.notes,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (
                        record.id,
                        record.name,
                        record.category,
                        record.subcategory,
                        record.kg_co2e_per_unit,
                        record.unit,
                        record.confidence,
                        record.source,
                        record.source_url,
                        record.region,
                        record.notes,
                    ),
                )
                upserts += 1

        connection.commit()
        return upserts
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed normalized emission factors into the CarbonDrop database.")
    parser.add_argument("--dataset-dir", type=Path, default=DATASET_DIR, help="Directory containing source CSV files.")
    args = parser.parse_args()

    if not args.dataset_dir.exists():
        raise SystemExit(f"Dataset directory not found: {args.dataset_dir}")

    count = seed_database(args.dataset_dir)
    print(f"Seeded/updated {count} emission factor rows from {args.dataset_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
