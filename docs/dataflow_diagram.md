# CarbonDrop Data Flow Diagram

## Overview

This document illustrates how data flows through the CarbonDrop system from user input to final carbon footprint calculations and reporting.

## High-Level Data Flow Diagram

```mermaid
flowchart TD
    subgraph "External Data Sources"
        DEFRA[DEFRA Emission Factors<br/>UK Government Data]
        EGRID[eGRID Electricity Factors<br/>EPA Data]
        Agribalyse[Agribalyse Food Data<br/>French LCA Database]
        OWID[Our World in Data<br/>Global Statistics]
        Custom[Custom Food Emissions<br/>Compiled Dataset]
    end

    subgraph "Data Ingestion & Processing"
        ETL[ETL Pipeline<br/>Data Normalization]
        Validation[Data Validation<br/>Unit Conversion]
        Indexing[Dataset Indexing<br/>Search Optimization]
    end

    subgraph "User Input"
        Image[Receipt Images<br/>JPG/PNG]
        Text[Manual Text Input<br/>Optional]
        Params[Simulation Parameters<br/>JSON]
    end

    subgraph "Processing Pipeline"
        OCR[OCR Engine<br/>Tesseract]
        Classification[Document Classifier<br/>Keyword Matching]
        Parsing[Specialized Parsers<br/>Regex Patterns]
        Normalization[Data Normalization<br/>Unit Conversion]
        Matching[Emission Matching<br/>Fuzzy Search]
        Calculation[Footprint Calculation<br/>Mathematical Operations]
    end

    subgraph "Data Storage"
        DB[(SQLite Database<br/>User Data)]
        Cache[(In-Memory Cache<br/>Session Data)]
        Files[(File Storage<br/>Uploaded Images)]
    end

    subgraph "Output & Reporting"
        API[REST API Responses<br/>JSON]
        Charts[Visualization Charts<br/>Chart.js]
        Reports[Footprint Reports<br/>PDF/CSV Export]
        Dashboard[Dashboard Analytics<br/>Aggregated Data]
    end

    subgraph "User Interface"
        Web[React Frontend<br/>SPA]
        Mobile[Mobile App<br/>Future]
    end

    %% Data flow connections
    DEFRA --> ETL
    EGRID --> ETL
    Agribalyse --> ETL
    OWID --> ETL
    Custom --> ETL

    ETL --> Validation
    Validation --> Indexing
    Indexing --> Matching

    Image --> OCR
    Text --> Parsing
    Params --> Calculation

    OCR --> Classification
    Classification --> Parsing
    Parsing --> Normalization
    Normalization --> Matching
    Matching --> Calculation

    Calculation --> DB
    Image --> Files
    Classification --> DB
    Parsing --> DB

    DB --> API
    DB --> Dashboard
    DB --> Reports

    API --> Web
    API --> Mobile
    Dashboard --> Web
    Reports --> Web
    Charts --> Web

    %% Styling
    classDef inputClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef processClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef storageClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef outputClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef externalClass fill:#ffebee,stroke:#d32f2f,stroke-width:2px

    class Image,Text,Params inputClass
    class OCR,Classification,Parsing,Normalization,Matching,Calculation,ETL,Validation,Indexing processClass
    class DB,Cache,Files storageClass
    class API,Charts,Reports,Dashboard outputClass
    class DEFRA,EGRID,Agribalyse,OWID,Custom externalClass
    class Web,Mobile outputClass
```

## Detailed Data Flow: Receipt Processing

```mermaid
flowchart TD
    A[User Uploads Image] --> B{File Validation}
    B -->|Valid| C[Store Original File]
    B -->|Invalid| D[Return Error]

    C --> E[OCR Processing]
    E --> F[Extract Raw Text]
    F --> G[Document Classification]

    G --> H{Document Type?}
    H -->|Grocery| I[Grocery Parser]
    H -->|Restaurant| J[Restaurant Parser]
    H -->|Utility| K[Utility Parser]
    H -->|Invoice| L[Invoice Parser]
    H -->|Transport| M[Transport Parser]

    I --> N[Extract Items, Quantities, Categories]
    J --> N
    K --> N
    L --> N
    M --> N

    N --> O[Data Normalization]
    O --> P[Unit Conversion<br/>kg/L/gallon standardization]

    P --> Q[Emission Factor Matching]
    Q --> R{Item Found in Dataset?}
    R -->|Yes| S[Retrieve CO2 Factor]
    R -->|No| T[Fuzzy String Matching]
    T --> U{Match Found?}
    U -->|Yes| S
    U -->|No| V[Category-based Estimation]
    V --> S

    S --> W[Calculate Footprint<br/>qty × factor × unit_conversion]
    W --> X[Aggregate Total CO2]

    X --> Y[Calculate EcoCredits<br/>Based on footprint sustainability]
    Y --> Z[Store in Database]

    Z --> AA[Generate Response]
    AA --> BB[Return JSON to Frontend]

    C --> Files[(File Storage)]
    Z --> DB[(Receipts & Items Tables)]
    G --> DB
    N --> DB
    X --> DB
    Y --> DB
```

## Data Flow: What-If Simulations

```mermaid
flowchart TD
    A[User Sets Parameters] --> B{Simulation Type?}

    B -->|Meat Replacement| C[Load Meat Emission Factors]
    B -->|Transport Switch| D[Load Transport Factors]
    B -->|Energy Efficiency| E[Load Energy Factors]
    B -->|Electric Vehicle| F[Load EV Factors]
    B -->|Local Food| G[Load Transport Factors]
    B -->|Waste Reduction| H[Load Waste Factors]

    C --> I[Calculate Current CO2<br/>meals × meat_factor]
    D --> J[Calculate Mode Comparison<br/>distance × mode_factor]
    E --> K[Calculate Energy Savings<br/>bulbs × hours × efficiency]
    F --> L[Calculate Fuel vs Electric<br/>km × efficiency × emission_factor]
    G --> M[Calculate Transport Savings<br/>meals × transport_reduction]
    H --> N[Calculate Waste Impact<br/>waste × emission_factor]

    I --> O[Compute Annual Savings]
    J --> O
    K --> O
    L --> O
    M --> O
    N --> O

    O --> P[Format Results<br/>JSON Response]
    P --> Q[Return to Frontend]

    C --> DS[(Emission Datasets)]
    D --> DS
    E --> DS
    F --> DS
    G --> DS
    H --> DS
```

## Data Flow: Dashboard Analytics

```mermaid
flowchart TD
    A[User Loads Dashboard] --> B[Authenticate User]
    B --> C[Query User Receipts]

    C --> D[Aggregate by Month<br/>SQL GROUP BY]
    D --> E[Calculate Trends<br/>Month-over-month change]

    C --> F[Query User Offsets<br/>Tree planting history]
    F --> G[Calculate Total Trees<br/>CO2 offset]

    C --> H[Query EcoCredits<br/>Current balance]
    H --> I[Calculate Badge Level<br/>Based on trees planted]

    E --> J[Format Chart Data<br/>{month, total} arrays]
    G --> K[Format Offset Data<br/>trees, offset_kg, badge]
    I --> L[Format Credit Data<br/>balance, level]

    J --> M[Combine Dashboard Data]
    K --> M
    L --> M

    M --> N[Return JSON Response]
    N --> O[Render Charts<br/>Chart.js visualization]
```

## Data Dictionary

### Input Data Types

| Data Type         | Source      | Format    | Validation                            |
| ----------------- | ----------- | --------- | ------------------------------------- |
| Receipt Images    | User Upload | JPG/PNG   | File size < 10MB, dimensions < 5000px |
| Simulation Params | User Form   | JSON      | Required fields, numeric ranges       |
| Authentication    | User Login  | JWT Token | Valid signature, not expired          |
| Manual Text       | User Input  | String    | Length < 1000 chars, no special chars |

### Processed Data Types

| Data Type             | Processing       | Output Format      | Storage                  |
| --------------------- | ---------------- | ------------------ | ------------------------ |
| OCR Text              | Tesseract        | String             | Temporary (not stored)   |
| Document Type         | Keyword Matching | Enum               | receipts.document_type   |
| Parsed Items          | Regex Patterns   | Array of Objects   | items table              |
| Normalized Quantities | Unit Conversion  | Float (kg/L/units) | items.qty, items.unit    |
| Matched Emissions     | Fuzzy Search     | Float (kgCO2e)     | items.footprint          |
| Total Footprint       | Summation        | Float (kgCO2e)     | receipts.total_footprint |
| EcoCredits            | Algorithm        | Integer            | users.eco_credits        |

### Output Data Types

| Data Type          | Consumer      | Format     | Update Frequency  |
| ------------------ | ------------- | ---------- | ----------------- |
| Receipt Analysis   | Frontend      | JSON       | Real-time         |
| Dashboard Data     | Frontend      | JSON Array | On page load      |
| Simulation Results | Frontend      | JSON       | On simulation run |
| Leaderboard        | Frontend      | JSON Array | Daily cache       |
| Export Data        | User Download | CSV/PDF    | On demand         |

## Data Storage Schema

### SQLite Tables

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE,
    password_hash VARCHAR,
    eco_credits INTEGER DEFAULT 0
);

-- Receipts table
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_footprint FLOAT,
    document_type VARCHAR,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Items table
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    receipt_id INTEGER REFERENCES receipts(id),
    name VARCHAR,
    matched_name VARCHAR,
    qty FLOAT,
    unit VARCHAR,
    footprint FLOAT,
    category VARCHAR DEFAULT 'food'
);

-- User offsets (tree planting)
CREATE TABLE user_offsets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    trees_planted INTEGER,
    co2_offset_kg FLOAT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Data Validation Rules

### Input Validation

- **File Upload**: MIME type check, size limits, image corruption detection
- **Text Input**: Length limits, XSS prevention, special character filtering
- **Numeric Parameters**: Range validation, type checking, null prevention

### Business Logic Validation

- **Quantities**: Must be positive, reasonable ranges (0.001 - 10000 kg)
- **Emission Factors**: Must exist in dataset, not null/zero
- **User Permissions**: JWT validation, user existence check
- **Credit Balance**: Sufficient funds for tree planting

## Error Handling Data Flow

```mermaid
flowchart TD
    A[Error Occurs] --> B{Error Type?}

    B -->|Validation Error| C[Return 400 Bad Request<br/>Field-specific message]
    B -->|Authentication Error| D[Return 401 Unauthorized<br/>Login required message]
    B -->|OCR Failure| E[Return 500 Internal Error<br/>Image quality message]
    B -->|Database Error| F[Return 500 Internal Error<br/>System error message]
    B -->|External API Error| G[Return 503 Service Unavailable<br/>Retry later message]

    C --> H[Log Error Details]
    D --> H
    E --> H
    F --> H
    G --> H

    H --> I[Frontend Displays<br/>User-Friendly Message]
    I --> J[User Takes Action<br/>Retry/Correct input]
```

## Performance Data Flow

```mermaid
flowchart TD
    A[Request Received] --> B[Start Performance Timer]

    B --> C[Process Request]
    C --> D[Database Queries]
    D --> E[External API Calls<br/>Optional]
    E --> F[Computation Logic]

    F --> G[Stop Timer]
    G --> H{Response Time < Threshold?}

    H -->|Yes| I[Return Success Response]
    H -->|No| J[Log Performance Warning]
    J --> I

    I --> K[Record Metrics<br/>Response time, success rate]
    K --> L[Update Monitoring Dashboard]
```

## Security Data Flow

```mermaid
flowchart TD
    A[Incoming Request] --> B[Extract Authorization Header]

    B --> C{Token Present?}
    C -->|No| D[Return 401 Unauthorized]

    C -->|Yes| E[Decode JWT Token]
    E --> F{Token Valid?}
    F -->|No| D

    F -->|Yes| G[Extract User ID]
    G --> H[Query User from Database]
    H --> I{User Exists?}
    I -->|No| D

    I -->|Yes| J[Check User Permissions]
    J --> K{Permissions OK?}
    K -->|No| L[Return 403 Forbidden]

    K -->|Yes| M[Process Request]
    M --> N[Log Access Event]
    N --> O[Return Response]
```

## Data Retention Policy

- **User Data**: Retained indefinitely unless user requests deletion
- **Receipt Images**: Stored for 1 year, then archived
- **Processing Logs**: Retained for 90 days
- **Analytics Data**: Aggregated and retained indefinitely
- **Temporary Files**: Deleted immediately after processing

## Backup and Recovery

- **Database**: Daily automated backups
- **File Storage**: Weekly backups of uploaded images
- **Configuration**: Version controlled, backed up with code
- **Recovery Time**: < 4 hours for database, < 24 hours for files

## Data Privacy Compliance

- **User Data**: Encrypted at rest, anonymized in analytics
- **Image Data**: Processed server-side, not stored with PII
- **Export Controls**: Users can request data deletion
- **Third-party Data**: Sourced from public government datasets
