# CarbonDrop — Multi-domain Architecture & Expansion Plan (Updated with dataset links)

> Expanded plan and actionable dataset links to help you grow CarbonDrop from grocery-only to a robust multi-domain footprint extractor.

---

## Quick summary

This document updates the architecture and expansion plan and adds **direct dataset download links** (public sources + notes on licensing) so you can populate an Emission Factor DB for multiple domains: food, transport, energy, products, and aviation.

---

## 1) High-level architecture (Mermaid)

```mermaid
flowchart TB
  U[User Upload / Mobile App / Email ingest] -->|image/pdf/text| OCR[OCR & Layout Parser]
  OCR --> DocClass[Document Classifier]
  DocClass -->|grocery| ParserG[Parser: Grocery Template]
  DocClass -->|restaurant| ParserR[Parser: Restaurant Template]
  DocClass -->|invoice| ParserI[Parser: Invoice Template]
  DocClass -->|utility| ParserU[Parser: Utility Template]

  ParserG --> Norm[Normalizer -> Unified Schema]
  ParserR --> Norm
  ParserI --> Norm
  ParserU --> Norm

  Norm --> Match[Emission Mapper]
  Match --> EFDB[Emission Factor DB (multi-source)]
  Match --> HumanLoop[Human-in-the-loop / Corrections]

  Match --> Store[Normalized Records DB (JSONB)]
  Store --> Report[Report Generator / Aggregation]
  Report --> UI[Frontend / Mobile]
  Report --> API[API / Export CSV]

  HumanLoop --> Match
  HumanLoop --> MLTrain[Retraining / Fine-tune]
  MLTrain --> DocClass
  MLTrain --> ParserG
  MLTrain --> Match

  subgraph Infra
    OCR
    DocClass
    Parsers[All Parser Modules]
    Norm
    Match
    EFDB
    Store
    Report
    HumanLoop
    MLTrain
  end
```

---

## 2) Actionable dataset links (by domain)

Below are **direct** dataset downloads and notes. Use these to seed your EFDB. I included licensing notes where available.

### Food / Agriculture

- **Agribalyse (French LCI for food)** — available via openLCA Nexus. Use for food item emission factors (you already have a CSV in the repo but official source is here).

  - Nexus page (download through openLCA Nexus): [https://nexus.openlca.org/database/Agribalyse](https://nexus.openlca.org/database/Agribalyse). (openLCA Nexus).

- **Poore & Nemecek (2018) dataset** — meta-analysis behind large food-footprint numbers. Useful for per-product footprints and averages (paper + dataset). PDF/full dataset: [https://josephpoore.com/Science%20360%206392%20987%20-%20Accepted%20Manuscript.pdf](https://josephpoore.com/Science%20360%206392%20987%20-%20Accepted%20Manuscript.pdf)

- **Our World in Data — food & environmental impacts** — curated data and downloadable CSVs that summarize many sources: [https://ourworldindata.org/environmental-impacts-of-food](https://ourworldindata.org/environmental-impacts-of-food)

  - OWID data repo (CO2 & related): [https://github.com/owid/co2-data](https://github.com/owid/co2-data)

- **FAOSTAT emissions intensities** — commodity-level emissions and methodology (downloadable PDFs and data exports): [https://files-faostat.fao.org/production/EI/EI_e.pdf](https://files-faostat.fao.org/production/EI/EI_e.pdf) and FAOSTAT portal for CSV extracts.

### Transport (road, taxi, car, public transport)

- **UK Government / DEFRA (GHG Conversion Factors)** — yearly Excel releases (condensed, full, and flat file for programmatic use). Direct downloads:

  - 2025 factors (condensed set & flat file): [https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025)
  - Direct condensed spreadsheet (example): [https://assets.publishing.service.gov.uk/media/6722566a3758e4604742aa1e/ghg-conversion-factors-2024-condensed_set**for_most_users**v1_1.xlsx](https://assets.publishing.service.gov.uk/media/6722566a3758e4604742aa1e/ghg-conversion-factors-2024-condensed_set__for_most_users__v1_1.xlsx)

- **EPA eGRID (US electricity generation / grid factors)** — useful when converting kWh to kgCO2e (US regional factors). Download page: [https://www.epa.gov/egrid](https://www.epa.gov/egrid) and detailed data: [https://www.epa.gov/egrid/detailed-data](https://www.epa.gov/egrid/detailed-data)

- **ICAO Carbon Emissions Calculator / Dataset (aviation)** — calculator + full dataset download options and API for flight emissions: [https://www.icao.int/environmental-protection/environmental-tools/icec](https://www.icao.int/environmental-protection/environmental-tools/icec) and ICEC API/full dataset info: [https://www.icao.int/environmental-protection/environmental-tools/icec/icec-api](https://www.icao.int/environmental-protection/environmental-tools/icec/icec-api)

### Energy & Utilities

- **eGRID (EPA)** — regional US electric grid emissions factors (xlsx): [https://www.epa.gov/egrid/detailed-data](https://www.epa.gov/egrid/detailed-data)
- **National Grid ESO (UK) Carbon Intensity API** — near-real-time grid intensity (for time-of-day electricity footprints): [https://carbonintensity.org.uk/](https://carbonintensity.org.uk/) (API docs on their site)
- **IEA / International Energy Agency** — country-level energy statistics (some data behind paywall) but IEA provides many public stats: [https://www.iea.org/data-and-statistics](https://www.iea.org/data-and-statistics)

### Product / Manufacturing (electronics, clothing, appliances)

- **ecoinvent** — industry-grade LCA database (commercial license required): [https://ecoinvent.org/](https://ecoinvent.org/) (see licensing)
- **openLCA Nexus** — repository with many LCA datasets (some free, some paid): [https://nexus.openlca.org/databases](https://nexus.openlca.org/databases)
- **Environdec / EPD databases** — product-specific Environmental Product Declarations (EPDs) — search portals like EPD International or EPDOnline depending on region.

### Global & Country-level datasets

- **Our World in Data / CO2 & GHG datasets** (global): [https://github.com/owid/co2-data](https://github.com/owid/co2-data)
- **EDGAR (JRC) GHG Emissions** — global emissions and inventories: [https://edgar.jrc.ec.europa.eu/report_2024](https://edgar.jrc.ec.europa.eu/report_2024)

### Notes on licensing & use

- **Open/public & CC / gov datasets (DEFRA, EPA, OWID, FAOSTAT)** are safe to ingest for building an EFDB (check local licensing/attribution).
- **Commercial LCA datasets (ecoinvent, some openLCA entries, certain EPDs)** require a license for production use — you can use them for research or evaluation if you have a license.

---

## 3) How to integrate these datasets (concrete steps)

1. **Seed EFDB with conservative, public sources first:** start with DEFRA flat file (transport, energy), Agribalyse (food) and eGRID (US grid). These provide good coverage for MVP domains.
2. **Normalize units**: convert everything to `kgCO2e` per _unit type_ you choose (kg_co2_per_kg, kg_co2_per_km, kg_co2_per_kWh, kg_co2_per_item). Store `original_source_url` and `last_updated` metadata.
3. **Add uncertainty bands**: where possible record `uncertainty_pct` so you can display ranges to users.
4. **Add locale variants**: e.g., grid intensity is country/region-specific; have a `locale` or `region` field and default fallbacks.
5. **Fallbacks**: for items missing exact matches, compute category averages (e.g., "red meat average", "vegetables average").

---

## 4) Detailed plan (phased, with datasets in each phase)

### Phase 0 — Immediate (1–2 weeks)

- Ingest DEFRA flat file + condensed set (transport, generic product emission factors) into EFDB.

  - Use: [https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025).

- Ingest Agribalyse (or use the CSV you already have) to cover food items.

  - Use: [https://nexus.openlca.org/database/Agribalyse](https://nexus.openlca.org/database/Agribalyse)

- Add per-region electricity factors using EPA eGRID (for US) and National Grid carbon intensity (UK) APIs.

  - EPA eGRID: [https://www.epa.gov/egrid/detailed-data](https://www.epa.gov/egrid/detailed-data)
  - UK carbon intensity API: [https://carbonintensity.org.uk/](https://carbonintensity.org.uk/)

Deliverables: EFDB seeded with food, transport, electricity factors; mapping scripts to normalize units.

### Phase 1 — MVP domains (3–6 weeks)

- Add dataset for aviation (ICAO ICEC) and build a flight-distance→CO2 calculator.

  - ICAO ICEC: [https://www.icao.int/environmental-protection/environmental-tools/icec](https://www.icao.int/environmental-protection/environmental-tools/icec)

- Add FAOSTAT commodity emission intensities for country-level fallbacks.

  - FAOSTAT docs/data: [https://files-faostat.fao.org/production/EI/EI_e.pdf](https://files-faostat.fao.org/production/EI/EI_e.pdf)

- Add Poore & Nemecek dataset for more granular food footprints (where useful): [https://josephpoore.com/Science%20360%206392%20987%20-%20Accepted%20Manuscript.pdf](https://josephpoore.com/Science%20360%206392%20987%20-%20Accepted%20Manuscript.pdf)

Deliverables: Restaurant parser + EF mapping, Flights module, country fallbacks.

### Phase 2 — Improve accuracy (6–12 weeks)

- Integrate embeddings-based matching and a vector DB (sentence-transformers or OpenAI embeddings + pgvector/Pinecone).
- Evaluate adding commercial LCA datasets (ecoinvent) where you need industrial-grade accuracy (purchase license if productizing).

  - ecoinvent: [https://ecoinvent.org/](https://ecoinvent.org/)

- Begin collecting human-corrected mappings to improve model matching.

Deliverables: Embedding matcher, labeled dataset, upgraded EFDB with licensed sources if purchased.

---

## 5) Example code snippets / templates (where to start)

- **DEFRA ingestion (Python)**: parse `flat file` Excel and convert rows to JSON with units and source URL.
- **Agribalyse**: if you already have CSV, create a canonical mapping table that links common grocery text (`milk 1L`, `whole milk`) → Agribalyse product IDs.
- **Flight module**: use ICAO distance matrix / ICEC API to convert flight routes to CO2e per passenger.

---

## 6) Testing data & evaluation

- Create small labeled corpora per domain (200–500 docs): restaurant bills, invoices, hotel receipts, fuel receipts, electricity bills.
- Evaluate end-to-end CO2 error (MAPE) vs human-labeled totals.

---

## 7) Next steps I can take for you

- I can **inject these dataset links and the normalized ingestion scripts** into your repo (example ETL scripts for DEFRA, Agribalyse, eGRID). Pick one and I will add starter code.
- Or I can **export this doc** as `.md` or `.pdf` for sharing.

---

_End of updated plan with dataset links._
