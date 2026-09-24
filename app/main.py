from fastapi import FastAPI, HTTPException, Query, Path, Depends, Request
from fastapi.responses import JSONResponse
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv

# Import database/service helper functions
from services.products import (
    get_all_products,
    add_product,
    remove_product,
    change_product,
    load_products,
)

# Import Pydantic models for request validation
from schema.product import Product, ProductUpdate 

# Load environment variables from .env file if available
load_dotenv()

# Initialize the main FastAPI application instance
app = FastAPI(
    title="E-Commerce Product API",
    description="A simple REST API for managing e-commerce products with FastAPI and Pydantic",
    version="1.0.0"
)


# ==========================================
# Dependencies & Health Check
# ==========================================

def common_logic():
    """Simple sample dependency function returning a greeting."""
    return "Hello World"


@app.get("/", response_model=dict)
def root(dep=Depends(common_logic)):
    """
    Root / Health Check endpoint.
    Demonstrates FastAPI's Depends() dependency injection system.
    """
    return JSONResponse(
        status_code=200,
        content={"message": "Welcome to FastAPI", "dependency": dep}
    )


# ==========================================
# Product Routes
# ==========================================

@app.get("/products", response_model=Dict)
def list_products(
    dep = Depends(load_products),
    name: str = Query(default=None, min_length=1, max_length=50, description="Search product by name (case-insensitive)"),
    short_by_price: bool = Query(default=False, description="Sort products by price"),
    order: str = Query(default='asc', description="Sort order when short_by_price=true ('asc' or 'desc')"),
    limit: int = Query(default=5, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip for pagination"),
):
    """
    Retrieves a paginated list of products with optional name filtering and price sorting.
    """
    products = dep

    # Filter products by search term (case-insensitive)
    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    # Return 404 if the search term yields no results
    if not products:
        raise HTTPException(status_code=404, detail=f"No products found matching name='{name}'")
    
    # Sort by price if requested
    if short_by_price:
        reverse = order.lower() == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(products)

    # Apply pagination slice
    products = products[offset: offset + limit]

    return {
        "total": total,
        "limit": limit,
        "items": products, 
    }


@app.get("/products/{product_id}", response_model=Dict)
def get_product_by_id(
    product_id: str = Path(..., min_length=36, max_length=36, description="UUID of the product (36 characters)")
): 
    """
    Fetches a single product by its UUID.
    Returns 404 if the product does not exist.
    """
    products = get_all_products()  

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found!")


@app.post("/products", status_code=201)
def create_product(product: Product):
    """
    Creates a new product record.
    - Validates incoming data using the Pydantic Product model.
    - Generates a new unique UUID and ISO creation timestamp.
    """
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return product.model_dump(mode="json")


@app.delete("/products/{product_id}")
def delete_product(product_id: UUID = Path(..., description="UUID of the product to delete")):
    """
    Deletes an existing product by its UUID.
    """
    try:
        res = remove_product(str(product_id))
        return res 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/products/{product_id}")
def update_product(
    product_id: UUID = Path(..., description="UUID of the product to update"),
    payload: ProductUpdate = ...
):
    """
    Partially updates an existing product.
    Only fields sent in the request body are modified.
    """
    try:
        updated = change_product(str(product_id), payload.model_dump(mode="json", exclude_unset=True))
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
