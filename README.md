# FastAPI E-Commerce API

A RESTful E-Commerce Product Management API built with FastAPI and Pydantic v2.

## Features

- **Product Listing & Filtering**: Filter by name (case-insensitive), sort by price (asc/desc), and paginate with `limit` and `offset`.
- **Product Retrieval**: Lookup products by UUID with path validation.
- **Product Creation & Updates**: Full schema validation with Pydantic:
  - Custom SKU format validation
  - Email domain validation for sellers
  - Business rule validations (e.g. stock vs. active status)
  - Computed fields (`final_price`, `volume_cm3`)
- **Product Deletion**: Delete products by UUID.
- **Interactive Documentation**: Auto-generated OpenAPI / Swagger UI at `/docs`.

## Project Structure

```text
Fastapi-ecommerce/
├── app/
│   ├── main.py              # FastAPI app & route definitions
│   ├── schema/
│   │   └── product.py       # Pydantic models and validators
│   ├── services/
│   │   └── products.py      # Business logic & file data storage
│   ├── data/
│   │   ├── products.json    # Product dataset
│   │   └── dummy.json       # Working data storage
│   └── requirements.txt
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Fastapi-ecommerce.git
cd Fastapi-ecommerce
```

### 2. Create and Activate a Virtual Environment

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
cd app
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 5. Interactive API Docs

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
