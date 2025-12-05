# CarbonDrop Sequence Diagram

## Overview

This document illustrates the detailed sequence of interactions during the receipt upload and carbon footprint calculation process in CarbonDrop.

## Receipt Upload Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant Auth as Auth Service
    participant OCR as OCR Service
    participant DC as Document Classifier
    participant DP as Document Parser
    participant EFM as Enhanced Footprint Matcher
    participant DB as SQLite Database
    participant DS as Emission Datasets

    Note over U,DS: Receipt Upload Process

    U->>FE: Select and upload receipt image
    FE->>FE: Validate file format and size
    FE->>BE: POST /upload_receipt (multipart/form-data)
    BE->>Auth: Verify JWT token
    Auth-->>BE: Token valid, return user info

    BE->>BE: Extract file from request
    BE->>OCR: extract_items_from_image(image_bytes)
    OCR->>OCR: Preprocess image (PIL)
    OCR->>OCR: Run Tesseract OCR
    OCR-->>BE: Raw text and extracted items

    BE->>DC: classify_document_from_image(image_bytes)
    DC->>DC: Preprocess image for classification
    DC->>DC: Extract text for keyword analysis
    DC->>DC: Pattern matching (grocery/restaurant/utility/invoice/transport)
    DC-->>BE: DocumentType enum

    BE->>DP: document_parser.parse_document(image_bytes)
    DP->>DP: Select appropriate parser based on DocumentType
    alt Grocery Receipt
        DP->>DP: GroceryParser.parse()
        DP->>DP: Extract items, quantities, categories
    else Restaurant Receipt
        DP->>DP: RestaurantParser.parse()
        DP->>DP: Extract menu items and prices
    else Utility Bill
        DP->>DP: UtilityParser.parse()
        DP->>DP: Extract consumption data (kWh, therms, gallons)
    else Invoice
        DP->>DP: InvoiceParser.parse()
        DP->>DP: Extract line items and amounts
    else Transport Ticket
        DP->>DP: TransportParser.parse()
        DP->>DP: Extract distances, fuel, routes
    end
    DP-->>BE: Structured items list with metadata

    BE->>BE: Normalize quantities (kg/L conversion)
    BE->>EFM: EnhancedFootprintMatcher.match_and_compute(items)

    EFM->>EFM: Load emission dataset (CSV)
    loop For each item
        EFM->>EFM: Find best match using multiple strategies
        alt Exact match found
            EFM->>EFM: Get emission factor from dataset
        else Fuzzy match
            EFM->>EFM: Apply fuzzy string matching (WRatio)
            EFM->>EFM: Category-specific filtering
        else Fallback matching
            EFM->>EFM: Semantic normalization
            EFM->>EFM: Cross-category search
        end

        EFM->>EFM: Calculate footprint (qty × emission_factor)
        EFM->>EFM: Apply unit conversions if needed
    end
    EFM-->>BE: Matched items with footprints and total CO2

    BE->>DB: Create Receipt record
    DB-->>BE: Receipt ID returned
    BE->>DB: Create Item records (bulk insert)
    DB-->>BE: Items saved

    BE->>BE: Calculate EcoCredits (based on footprint)
    BE->>DB: Update user.eco_credits (+= credits)
    DB-->>BE: Credits updated

    BE-->>FE: JSON response with receipt data, items, total footprint
    FE->>FE: Update UI with results
    FE->>FE: Render charts (Chart.js)
    FE->>FE: Display analysis breakdown

    Note over FE: Process Complete - User sees carbon footprint analysis
```

## Authentication Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as SQLite Database

    Note over U,DB: User Authentication Flow

    U->>FE: Enter login credentials
    FE->>FE: Basic form validation
    FE->>BE: POST /auth/login (username, password)

    BE->>DB: Query user by username
    DB-->>BE: User record or None

    alt User exists
        BE->>BE: Verify password hash
        alt Password correct
            BE->>BE: Generate JWT token
            BE->>BE: Set token expiration
            BE-->>FE: JWT token + user info
            FE->>FE: Store token in localStorage
            FE->>FE: Update login state
            FE-->>U: Redirect to dashboard
        else Password incorrect
            BE-->>FE: 401 Unauthorized
            FE-->>U: Display error message
        end
    else User not found
        BE-->>FE: 401 Unauthorized
        FE-->>U: Display error message
    end
```

## What-If Simulation Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant WS as WhatIfSimulator
    participant DS as Emission Datasets

    Note over U,DS: Simulation Process

    U->>FE: Configure simulation parameters
    U->>FE: Click "Simulate" button
    FE->>FE: Validate input parameters
    FE->>BE: POST /simulate_meat_replacement (params)

    BE->>WS: WhatIfSimulator.simulate_meat_replacement(params)
    WS->>DS: Load emission factors for beef and lentils
    DS-->>WS: CO2 factors returned

    WS->>WS: Calculate weekly meat CO2 consumption
    WS->>WS: Calculate weekly plant-based CO2 consumption
    WS->>WS: Compute weekly and annual savings
    WS-->>BE: Simulation results

    BE-->>FE: JSON with savings calculations
    FE->>FE: Display results in UI
    FE->>FE: Update charts/tables

    Note over FE: Simulation complete - User sees potential CO2 savings
```

## Tree Planting Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as SQLite Database

    Note over U,DB: Virtual Tree Planting Flow

    U->>FE: Click "Plant Trees" button
    FE->>BE: POST /plant_trees (JWT token)

    BE->>BE: Verify authentication
    BE->>DB: Query user's total carbon footprint
    DB-->>BE: Sum of all receipt footprints

    BE->>BE: Calculate trees needed (CO2 / 21 kg/tree/year)
    BE->>BE: Check user's EcoCredits balance
    DB-->>BE: Current credit balance

    alt Sufficient credits
        BE->>BE: Calculate affordable trees (credits / 100)
        BE->>BE: Deduct credits from user
        BE->>DB: Update user.eco_credits (-= cost)
        BE->>DB: Create UserOffset record
        DB-->>BE: Offset record created

        BE->>BE: Calculate new badge level
        BE-->>FE: Success response with tree count, offset, badge
        FE->>FE: Update UI with new balance and achievements
        FE-->>U: Show success message
    else Insufficient credits
        BE-->>FE: 400 Bad Request (insufficient credits)
        FE-->>U: Display error message
    end
```

## Dashboard Data Retrieval Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as SQLite Database

    Note over U,DB: Dashboard Loading

    U->>FE: Navigate to dashboard
    FE->>BE: GET /dashboard (JWT token)

    BE->>BE: Verify authentication
    BE->>DB: Query monthly footprint aggregation
    DB-->>BE: Monthly totals (SQL GROUP BY)

    BE-->>FE: Array of {month, total} objects
    FE->>FE: Process data for charts
    FE->>FE: Render Chart.js visualization

    Note over FE: Dashboard displayed with monthly carbon footprint trends
```

## Error Handling Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant OCR as OCR Service

    Note over U,OCR: Error Handling Example

    U->>FE: Upload corrupted image
    FE->>BE: POST /upload_receipt

    BE->>OCR: extract_items_from_image()
    OCR->>OCR: Attempt OCR processing
    OCR-->>BE: Exception (OCR failure)

    BE->>BE: Catch exception
    BE-->>FE: 500 Internal Server Error with message
    FE->>FE: Display user-friendly error message
    FE->>U: "OCR processing failed. Please try a clearer image."

    Note over FE: Error gracefully handled, user guided to resolution
```

## Performance Considerations

### Synchronous Processing

- Current implementation processes uploads synchronously
- OCR and classification happen sequentially
- Total processing time: 5-15 seconds for typical receipt

### Future Asynchronous Processing

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant Q as Task Queue (Celery)
    participant W as Worker Process

    U->>FE: Upload receipt
    FE->>BE: POST /upload_receipt
    BE->>Q: Queue processing task
    BE-->>FE: Immediate response (task ID)

    Q->>W: Assign task to worker
    W->>W: Process OCR, classification, parsing
    W->>W: Calculate footprint
    W->>DB: Save results
    W->>Q: Mark task complete

    FE->>BE: Poll /task_status/{task_id}
    BE->>Q: Check task status
    Q-->>BE: Status update
    BE-->>FE: Processing complete
    FE->>FE: Fetch and display results
```

## Security Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as SQLite Database

    Note over U,DB: Security Validation

    U->>FE: Access protected endpoint
    FE->>BE: GET /protected_endpoint (Authorization: Bearer {token})

    BE->>BE: Extract JWT from header
    BE->>BE: Decode and validate token
    alt Token valid
        BE->>BE: Extract user_id from token
        BE->>DB: Verify user exists and is active
        DB-->>BE: User confirmed
        BE->>BE: Check endpoint permissions
        BE-->>FE: Protected data
    else Token invalid/expired
        BE-->>FE: 401 Unauthorized
        FE->>FE: Redirect to login
    end
```

## Database Transaction Sequence

```mermaid
sequenceDiagram
    participant BE as FastAPI Backend
    participant DB as SQLite Database

    Note over BE,DB: Transaction Safety

    BE->>DB: BEGIN TRANSACTION
    BE->>DB: INSERT INTO receipts (...)
    DB-->>BE: Receipt ID

    loop For each item
        BE->>DB: INSERT INTO items (...)
    end
    DB-->>BE: Items inserted

    BE->>DB: UPDATE users SET eco_credits = eco_credits + ?
    DB-->>BE: Credits updated

    alt All operations successful
        BE->>DB: COMMIT
        DB-->>BE: Transaction committed
    else Any operation fails
        BE->>DB: ROLLBACK
        DB-->>BE: Transaction rolled back
        BE->>BE: Raise exception
    end
```

## API Response Format

### Successful Upload Response

```json
{
  "id": 123,
  "user_id": 456,
  "total_footprint": 15.67,
  "document_type": "grocery",
  "items": [
    {
      "name": "Organic Milk 2L",
      "matched_name": "milk",
      "qty": 2.0,
      "unit": "kg",
      "footprint": 2.34,
      "category": "food"
    }
  ],
  "date": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "detail": "OCR failed: Unable to extract text from image. Please ensure the image is clear and well-lit."
}
```

## Performance Metrics

- **OCR Processing**: 2-5 seconds
- **Document Classification**: < 1 second
- **Parsing**: 1-3 seconds
- **Footprint Matching**: < 1 second
- **Database Operations**: < 0.5 seconds
- **Total Response Time**: 5-15 seconds

## Monitoring Points

- JWT token validation success/failure
- OCR success rate by image quality
- Document classification accuracy
- Database query performance
- API response times by endpoint
- Error rates and types
