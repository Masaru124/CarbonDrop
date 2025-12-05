# CarbonDrop Documentation

## Overview

CarbonDrop is a comprehensive multi-domain carbon footprint calculator that processes receipts, invoices, utility bills, and transport documents to calculate environmental impact. The system uses advanced OCR, document classification, specialized parsers, and emission factor matching to provide accurate carbon footprint analysis across multiple domains including food, transport, energy, and utilities.

## Features

- **Multi-Domain Support**: Processes grocery receipts, restaurant bills, utility statements, invoices, and transport tickets
- **Advanced OCR**: Tesseract-powered text extraction with image preprocessing
- **Smart Classification**: Automatic document type detection using keyword patterns
- **Specialized Parsers**: Domain-specific parsing for accurate data extraction
- **Emission Matching**: Fuzzy string matching against comprehensive emission factor databases
- **What-If Simulations**: Interactive calculators for sustainable behavior changes
- **Gamification**: EcoCredits system with virtual tree planting for carbon offset
- **Analytics Dashboard**: Monthly footprint tracking and peer comparisons
- **REST API**: FastAPI-based backend with automatic OpenAPI documentation

## Architecture

### System Components

```
CarbonDrop/
├── app/                    # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main application
│   │   └── ...
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── database.py     # Database configuration
│   │   ├── auth.py         # Authentication
│   │   ├── ocr.py          # OCR processing
│   │   ├── parsers.py      # Document parsers
│   │   ├── footprint.py    # Emission calculations
│   │   └── ...
│   └── dataset/            # Emission factor datasets
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

### Technology Stack

**Backend:**

- **Framework**: FastAPI (Python async web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **OCR**: Tesseract with pytesseract
- **Image Processing**: PIL (Pillow)
- **Text Matching**: RapidFuzz
- **Authentication**: JWT (JSON Web Tokens)

**Frontend:**

- **Framework**: React 18 with Vite
- **Routing**: React Router
- **Styling**: Tailwind CSS
- **Charts**: Chart.js
- **HTTP Client**: Fetch API

**Infrastructure:**

- **Deployment**: Local development with uvicorn
- **Environment**: Python virtual environment
- **Package Management**: pip (backend), npm (frontend)

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Tesseract OCR (system installation required)

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd CarbonDrop
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**

   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

5. **Set up environment variables** (optional)

   ```bash
   export DATABASE_URL="sqlite:///./carbondrop.db"
   export SECRET_KEY="your-secret-key-here"
   ```

6. **Run database migrations**
   ```bash
   python -c "from backend.app.database import engine; from backend.app.models import Base; Base.metadata.create_all(bind=engine)"
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd app
   ```

2. **Install Node.js dependencies**

   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

### Running the Application

1. **Start the backend server**

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend server** (in another terminal)

   ```bash
   cd app
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Documentation

### Authentication Endpoints

#### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword"
}
```

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword"
}
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "eco_credits": 10
  }
}
```

### Document Processing Endpoints

#### Upload Receipt

```http
POST /upload_receipt
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>
```

Response:

```json
{
  "id": 123,
  "user_id": 1,
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

### Simulation Endpoints

#### Meat Replacement Simulation

```http
POST /simulate_meat_replacement
Content-Type: application/json

{
  "meat_meals_per_week": 3,
  "weeks": 52
}
```

Response:

```json
{
  "scenario": "Replace 3 meat meals/week with plant-based",
  "weekly_savings": 4.2,
  "annual_savings": 218.4,
  "meat_co2_per_week": 6.3,
  "plant_co2_per_week": 2.1
}
```

#### Transport Switch Simulation

```http
POST /simulate_transport_switch
Content-Type: application/json

{
  "trips_per_year": 4,
  "distance_per_trip_km": 500,
  "from_mode": "flight",
  "to_mode": "train"
}
```

#### Energy Efficiency Simulation

```http
POST /simulate_energy_efficiency
Content-Type: application/json

{
  "current_bulbs": 10,
  "led_bulbs": 10,
  "hours_per_day": 4,
  "days_per_year": 365
}
```

#### Electric Vehicle Simulation

```http
POST /simulate_electric_vehicle
Content-Type: application/json

{
  "annual_km": 15000,
  "current_fuel_efficiency": 10,
  "ev_efficiency": 0.2
}
```

#### Local Food Simulation

```http
POST /simulate_local_food
Content-Type: application/json

{
  "imported_meals_per_week": 10,
  "local_reduction_percent": 50,
  "weeks": 52
}
```

#### Waste Reduction Simulation

```http
POST /simulate_waste_reduction
Content-Type: application/json

{
  "current_waste_kg_per_week": 5,
  "reduction_percent": 30,
  "weeks": 52
}
```

### Dashboard and Analytics

#### Get Dashboard Data

```http
GET /dashboard
Authorization: Bearer <token>
```

Response:

```json
[
  {
    "month": "2024-01",
    "total": 45.67
  },
  {
    "month": "2024-02",
    "total": 38.92
  }
]
```

#### Get Leaderboard

```http
GET /leaderboard
Authorization: Bearer <token>
```

Response:

```json
[
  {
    "username": "ecowarrior",
    "score": 1250.5
  },
  {
    "username": "greenuser",
    "score": 980.3
  },
  {
    "username": "Average Household",
    "score": 4500.0
  }
]
```

### Gamification Endpoints

#### Plant Trees

```http
POST /plant_trees
Authorization: Bearer <token>
```

Response:

```json
{
  "message": "Successfully planted 2 virtual trees to offset 42.0 kg CO₂!",
  "trees_planted": 2,
  "carbon_footprint_offset": 42.0,
  "co2_offset_kg": 42.0,
  "badge": {
    "badge": "🌲 Tree Champion",
    "level": "Advanced"
  },
  "remaining_eco_credits": 80
}
```

#### Get User Offsets

```http
GET /user_offsets
Authorization: Bearer <token>
```

Response:

```json
{
  "total_trees": 5,
  "total_offset": 105.0,
  "badge": "🌲 Tree Champion",
  "level": "Advanced"
}
```

### History and Reports

#### Get Footprint History

```http
GET /footprint_history
Authorization: Bearer <token>
```

Response:

```json
[
  {
    "id": 123,
    "user_id": 1,
    "total_footprint": 15.67,
    "document_type": "grocery",
    "items": [...],
    "date": "2024-01-15T10:30:00Z"
  }
]
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    eco_credits INTEGER DEFAULT 0
);
```

### Receipts Table

```sql
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_footprint REAL NOT NULL,
    document_type VARCHAR(20) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Items Table

```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    matched_name VARCHAR(200),
    qty REAL NOT NULL,
    unit VARCHAR(20),
    footprint REAL NOT NULL,
    category VARCHAR(20) DEFAULT 'food',
    FOREIGN KEY (receipt_id) REFERENCES receipts (id)
);
```

### User Offsets Table

```sql
CREATE TABLE user_offsets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trees_planted INTEGER NOT NULL,
    co2_offset_kg REAL NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Emission Datasets

### Data Sources

CarbonDrop uses multiple authoritative sources for emission factors:

1. **DEFRA (UK Government)**: Comprehensive greenhouse gas conversion factors
2. **eGRID (EPA)**: US electricity grid emission factors
3. **Agribalyse**: French agricultural LCA database
4. **Our World in Data**: Global environmental statistics
5. **Custom Compiled**: Additional food and product emissions

### Dataset Format

Emission datasets are stored as CSV files with the following columns:

```csv
item,co2,unit,category,source,last_updated
"beef",27.0,kg,food,DEFRA,2024-01-01
"chicken",6.9,kg,food,DEFRA,2024-01-01
"electricity",0.207,kWh,energy,eGRID,2024-01-01
```

### Loading Datasets

Datasets are loaded automatically by the `load_dataset()` function in `footprint.py`:

```python
from backend.app.footprint import load_dataset

# Load the comprehensive dataset
dataset_path = "backend/dataset/combined_food_emissions.csv"
df = load_dataset(dataset_path)
```

## Frontend Components

### Main Components

- **App.jsx**: Main application with routing
- **Upload.jsx**: Document upload and analysis interface
- **History.jsx**: Footprint history viewer
- **Dashboard.jsx**: Monthly analytics dashboard
- **Leaderboard.jsx**: User ranking system
- **Simulator.jsx**: What-if scenario calculators
- **Login/Register**: Authentication forms

### Key Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Charts**: Chart.js integration for data visualization
- **Form Validation**: Client-side validation with error handling
- **Loading States**: User feedback during API calls
- **Error Handling**: Graceful error display and recovery

## Deployment

### Development

1. **Backend**: Use `uvicorn` with auto-reload

   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend**: Use Vite dev server
   ```bash
   cd app && npm run dev
   ```

### Production

1. **Build Frontend**

   ```bash
   cd app
   npm run build
   ```

2. **Serve Static Files**

   - Copy `dist/` to web server
   - Configure reverse proxy to FastAPI

3. **Database Migration**

   - Use production database (PostgreSQL recommended)
   - Run migrations for schema updates

4. **Environment Variables**
   ```bash
   DATABASE_URL="postgresql://user:pass@localhost/db"
   SECRET_KEY="production-secret-key"
   CORS_ORIGINS="https://yourdomain.com"
   ```

## Configuration

### Environment Variables

| Variable         | Default                     | Description                  |
| ---------------- | --------------------------- | ---------------------------- |
| `DATABASE_URL`   | `sqlite:///./carbondrop.db` | Database connection string   |
| `SECRET_KEY`     | `dev-secret-key`            | JWT signing key              |
| `CORS_ORIGINS`   | `http://localhost:5173`     | Allowed CORS origins         |
| `TESSERACT_PATH` | System default              | Path to Tesseract executable |

### Application Settings

Modify `backend/app/main.py` for application-wide settings:

```python
app = FastAPI(
    title="CarbonDrop API",
    description="Multi-domain carbon footprint calculator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

## Testing

### Backend Testing

```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing

```bash
cd app
npm test
```

### Manual Testing

1. **Upload Test Images**: Use sample receipts of different types
2. **API Endpoints**: Test with tools like Postman or curl
3. **User Flows**: Complete registration → upload → analysis → simulation cycle

## Troubleshooting

### Common Issues

1. **OCR Failures**

   - Ensure Tesseract is installed correctly
   - Check image quality (resolution, lighting)
   - Verify supported image formats

2. **Database Errors**

   - Check file permissions for SQLite database
   - Ensure database schema is up to date
   - Verify foreign key constraints

3. **Authentication Issues**

   - Check JWT token expiration
   - Verify SECRET_KEY consistency
   - Ensure proper token format in requests

4. **Frontend Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify all dependencies are installed

### Logs and Debugging

- **Backend Logs**: Check uvicorn output for errors
- **Frontend Logs**: Use browser developer tools
- **Database Logs**: Enable SQLAlchemy echo for query debugging

```python
# Enable SQL debugging
engine = create_engine(DATABASE_URL, echo=True)
```

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Make changes and test**
4. **Submit a pull request**

### Code Style

- **Backend**: Follow PEP 8 guidelines
- **Frontend**: Use ESLint and Prettier
- **Commits**: Use conventional commit format

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- **Documentation**: Check this README and inline code comments
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for general questions

## Roadmap

### Phase 1 (Current)

- ✅ Multi-domain document processing
- ✅ Basic emission factor matching
- ✅ What-if simulations
- ✅ Gamification system

### Phase 2 (Next)

- 🔄 Mobile application
- 🔄 Advanced ML matching
- 🔄 Real-time carbon intensity
- 🔄 Social features

### Phase 3 (Future)

- 🔄 IoT device integration
- 🔄 Advanced analytics
- 🔄 Carbon budgeting
- 🔄 Enterprise features

---

**CarbonDrop** - Making carbon footprint tracking accessible and actionable for everyone.
