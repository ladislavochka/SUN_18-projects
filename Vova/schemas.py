from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class BrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: Optional[str] = None
    description: Optional[str] = None

class BrandResponse(BrandCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: str
    price: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    brand_id: int

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    price: Optional[float]
    description: Optional[str]
    brand_id: int
    owner_id: int
    brand: BrandResponse

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    brand_id: Optional[int] = None
