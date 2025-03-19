# Order Price Calculator API

A FastAPI application that calculates order prices with a promotion engine using PostgreSQL database.

## Project Structure

```
~/Projects/order-price-calculator/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   └── price_calculator.py  # Business logic
├── .env                 # Environment variables
├── .dockerignore        # Docker ignore rules
├── docker-compose.yml   # Docker services configuration
├── Dockerfile          # FastAPI app container configuration
├── init_db.py         # Database initialization script
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Prerequisites

- Docker
- Docker Compose

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url> ~/Projects/order-price-calculator
cd ~/Projects/order-price-calculator
```

2. Start the application with Docker Compose:
```bash
docker-compose up --build
```

This will:
- Build the FastAPI application container
- Start a PostgreSQL database container
- Initialize the database with required tables
- Start the application on http://localhost:8000

To stop the application:
```bash
docker-compose down
```

To remove all data including the database volume:
```bash
docker-compose down -v
```

## Development Setup (Without Docker)

If you prefer to run the application without Docker, you'll need:
- Python 3.8+
- PostgreSQL 12+
- pip (Python package installer)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostgreSQL in `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=price_calculator
DB_USER=postgres
DB_PASSWORD=postgres
```

3. Initialize the database:
```bash
python init_db.py
```

4. Start the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Calculate Price
```bash
POST /calculate-price

Request body:
{
    "user_id": 123,
    "services": [
        {"id": 1, "name": "Cleaning", "price": 40},
        {"id": 2, "name": "Repair", "price": 60}
    ],
    "promo_code": "WELCOME10",
    "location": "Barcelona"
}

Response:
{
    "original_price": 100,
    "discount_applied": 30,
    "final_price": 70,
    "promotion_used": "BARCELONA30"
}
```

### Create Promotion
```bash
POST /promotions/

Request body:
{
    "code": "WELCOME10",
    "type": "fixed",
    "value": 10,
    "min_order": 0,
    "expiry_date": "2025-12-31"
}
```

### List Promotions
```bash
GET /promotions/
```

## Promotion Types

The system supports two types of promotions:
1. Fixed amount discount (type: "fixed")
2. Percentage discount (type: "percentage")

## Built-in Promotions

The system comes with three default promotions:
- WELCOME10: €10 fixed discount
- BARCELONA30: 30% off for orders in Barcelona
- MIN50: €5 off for orders above €50

## Error Handling

The API includes proper error handling for:
- Invalid promotion codes
- Expired promotions
- Minimum order requirements
- Database connection issues

## Development

The application uses:
- FastAPI for the web framework
- SQLAlchemy for database ORM
- Pydantic for data validation
- PostgreSQL for data storage

