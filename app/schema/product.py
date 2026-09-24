from pydantic import BaseModel, Field, AnyUrl, field_validator, model_validator, computed_field, EmailStr
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime


# ==========================================
# 1. Models for Creating / Storing Products
# ==========================================

class dimensions_cm(BaseModel):
    """Product physical dimensions in centimeters."""
    length: Annotated[float, Field(gt=0, strict=True, description="Length in cm")]
    width:  Annotated[float, Field(gt=0, strict=True, description="Width in cm")]
    height: Annotated[float, Field(gt=0, strict=True, description="Height in cm")]

    
class Seller(BaseModel):
    """Seller information and contact details."""
    id: UUID
    
    name: Annotated[
        str,
        Field(min_length=2, max_length=60, title="Seller Name", description="Name of the seller (2-60 chars)", examples=["mi store", "apple store"])
    ]

    email: EmailStr
    website: AnyUrl

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):
        """Restrict seller registrations to approved email domains only."""
        allowed_domains = ['mistore.in', 'gmail.com', 'apple.com']
        domain = str(value).split("@")[-1].lower()

        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed: {domain}")
        
        return value


class Product(BaseModel):
    """
    Main product model used when creating a new product or returning full details.
    Includes validation for SKU format, pricing, and business logic.
    """
    id: UUID
    sku: Annotated[
        str, 
        Field(min_length=6, max_length=30, title="SKU", description="Stock Keeping Unit", examples=["85asd-as5d46-001"])
    ]
    
    name: Annotated[
        str,
        Field(min_length=3, max_length=80, title="Product Name", description="Readable product name (3-80 chars)", examples=["Samsung Model Max"])
    ]

    description: Annotated[
        str,
        Field(max_length=200, description="Short product description")
    ]

    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=30,
            description="Category like mobile/laptops/electronics",
            examples=["mobile", "laptops"]
        )
    ]

    brand: Annotated[
        str,
        Field(min_length=2, max_length=40, examples=["samsung", "apple"])
    ]

    price: Annotated[
        float,
        Field(gt=0, strict=True, description="Base price in INR")
    ]

    currency: Literal["INR"] = "INR"

    discounted_percent: Annotated[
        int,
        Field(ge=0, le=98, description="Discount in percent (0-98)")
    ] = 0

    stock: Annotated[int, Field(ge=0, description="Available inventory stock (>=0)")]

    is_active: Annotated[bool, Field(description="Is product active and visible to buyers?")]

    rating: Annotated[
        float,
        Field(ge=0, le=5, strict=True, description="Customer rating out of 5")
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Up to 10 product search tags")
    ]

    image_urls: Annotated[
        List[AnyUrl],
        Field(default=None, max_length=10, description="List of product image URLs")
    ]

    dimensions_cm: dimensions_cm
    seller: Seller
    created: datetime

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value: str):
        """
        Ensures the SKU follows the standard pattern:
        - Must contain at least one hyphen '-'
        - Must end with a 3-digit sequence (e.g. -001, -123)
        """
        if "-" not in value:
            raise ValueError("SKU must contain '-'")

        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit sequence like -123")

        return value

    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "Product"):
        """Cross-field business validation across multiple attributes."""
        # Rule 1: Out of stock products cannot be marked active
        if model.stock == 0 and model.is_active is True:
            raise ValueError("if the stock is 0 then is_active must be False")

        # Rule 2: Items on discount must already have a customer rating
        if model.discounted_percent > 0 and model.rating == 0:
            raise ValueError("Discounted product must have a rating (rating != 0)")

        return model

    @computed_field
    @property
    def final_price(self) -> float:
        """Dynamically calculates the price after applying discount percentage."""
        return round(self.price * (1 - self.discounted_percent / 100), 2)

    @computed_field
    @property
    def volume_cm3(self) -> float:
        """Calculates total package volume in cubic centimeters."""
        d = self.dimensions_cm
        return round(d.length * d.width * d.height, 2)


# ==========================================
# 2. Models for Updating Products (Partial)
# ==========================================

class dimensions_cm_update(BaseModel):
    """Optional dimension fields for partial updates."""
    length: Optional[float] = Field(default=None, gt=0)
    width:  Optional[float] = Field(default=None, gt=0)
    height: Optional[float] = Field(default=None, gt=0)

  
class SellerUpdate(BaseModel):
    """Optional seller fields for partial updates."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=60)
    email: Optional[EmailStr] = None
    website: Optional[AnyUrl] = None


class ProductUpdate(BaseModel):    
    """
    Schema for PUT/PATCH product updates.
    All fields are optional, so clients only need to send the fields they wish to change.
    """
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = None
    brand: Optional[str] = None

    price: Optional[float] = Field(default=None, gt=0)
    currency: Optional[Literal["INR"]] = None

    discounted_percent: Optional[int] = Field(default=None, ge=0, le=99)
    stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)

    tags: Optional[List[str]] = Field(default=None, max_length=10)
    image_urls: Optional[List[AnyUrl]] = None

    dimensions_cm: Optional[dimensions_cm_update] = None
    seller: Optional[SellerUpdate] = None

    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "ProductUpdate"):
        """Validates business rules only on fields that were actually provided in the update."""
        if model.stock is not None and model.is_active is not None:
            if model.stock == 0 and model.is_active is True:
                raise ValueError("if the stock is 0 then is_active must be False")

        if model.discounted_percent is not None and model.rating is not None:
            if model.discounted_percent > 0 and model.rating == 0:
                raise ValueError("Discounted product must have a rating (rating != 0)")

        return model