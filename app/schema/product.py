from pydantic import BaseModel, Field, AnyUrl, field_validator, model_validator, computed_field, EmailStr
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime



#  CREATE PYDANTIC
class dimensions_cm(BaseModel):
    length: Annotated[float, Field(gt=0, strict=True, description="Length in cm")]
    width:  Annotated[float, Field(gt=0, strict=True, description="Width in cm")]
    height: Annotated[float, Field(gt=0, strict=True, description="Height in cm")]

    
class Seller(BaseModel):
    id: UUID
    
    name: Annotated[
            str,
            Field(min_length=2, max_length=60, title="Seller Name", description="Name of the seller(2-60 chars  )", examples=["mi store", "apple store"])
        ]

    email: EmailStr

    website: AnyUrl

    @field_validator("email", mode="after") # mode="after" means with the help of pydantic value convert into the sutaible datatype
    @classmethod  # Field_validator only validate the feild not validate them
    def validate_seller_email_domain(cls, value: EmailStr):

        allowed_domains=[
            'mistore.in', 'gmail.com', "apple.com"
        ]

        domain = str(value).split("@")[-1].lower()

        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed: {domain}")
        
        return value


class Product(BaseModel):
    id: UUID
    sku: Annotated[
            str, 
            Field(min_length=6, max_length=30, title="SKU", description="Stock Keeping Unit", examples=["85asd-as5d46-as6da"])
        ]
    
    name: Annotated[
            str,
            Field(min_length=3, max_length=80, title="Product Name", description="Readbale product name(3-80 char)", examples=["Samsung Model Max"])
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
            description="category like mobiles/laptop/electronics",
            examples=["mobile", "laptops"]
        )
    ]

    brand: Annotated[
        str,
        Field(min_length=2, max_length=40, examples=["samsung", "apple"])
    ]

    price: Annotated[
        float,
        Field(gt=0, strict=True, description="base price(INR)")
    ]

    currency: Literal["INR"] = "INR"

    discounted_percent: Annotated[
        int,
        Field(ge=0, le=98, description="Discount in percent (0-90)")
    ] = 0


    stock: Annotated[int, Field(ge=0, description="Available stock (>=0)")]

    is_active: Annotated[bool, Field(description="Is product active?")]

    rating: Annotated[
        float,
        Field(ge=0, le=5, strict=True, description="Rating out of 5")
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Up to 10 tags")
    ]

    image_urls: Annotated[
        List[AnyUrl],
        Field(default=None, max_length=10, description="Atleast 1 image URL")
    ]

    dimensions_cm: dimensions_cm

    seller: Seller

    created: datetime


    @field_validator("sku", mode="after") # mode="after" means with the help of pydantic value convert into the sutaible datatype
    @classmethod  # Field_validator only validate the feild not validate them
    def validate_sku_format(cls, value: str):
        if "-" not in value:
            raise ValueError("SKU must contain '-'")

        last = value.split("-")[-1]

        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digits sequence like -123")

        return value

    @model_validator(mode="after") # model_validator only validate the feild not validate them
    @classmethod
    def validate_business_rules(cls, model:"Product"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("if the stock is 0 then is_active must be False")

        if model.discounted_percent > 0 and model.rating == 0:
            raise ValueError("Discounted product must have a rating (rating != 0)")

        return model


    @computed_field
    @property # create new feild
    def final_price(self) -> float:
        return round(self.price * (1 - self.discounted_percent / 100), 2)

    @computed_field
    @property
    def volume_cm3(self) -> float:
        d = self.dimensions_cm
        return round(d.length * d.width * d.height, 2)



#  UPDATE PYDANTIC
class dimensions_cm_update(BaseModel):
    length: Optional[float] = Field(default=None, gt=0)
    width:  Optional[float] = Field(default=None, gt=0)
    height: Optional[float] = Field(default=None, gt=0)
  
class SellerUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=60)
    email: Optional[EmailStr] = None
    website: Optional[AnyUrl] = None

class ProductUpdate(BaseModel):    
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
        if model.stock is not None and model.is_active is not None:
            if model.stock == 0 and model.is_active is True:
                raise ValueError("if the stock is 0 then is_active must be False")

        if model.discounted_percent is not None and model.rating is not None:
            if model.discounted_percent > 0 and model.rating == 0:
                raise ValueError("Discounted product must have a rating (rating != 0)")

        return model

    