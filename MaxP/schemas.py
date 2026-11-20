from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ---------- Користувачі ----------
class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        # bcrypt бере максимум 72 байти, а кирилиця важить по 2 байти на символ
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Пароль задовгий (максимум 72 байти)")
        return v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Книги ----------
def _blank_to_none(v):
    if isinstance(v, str) and not v.strip():
        return None
    return v


class BookBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    genre: Optional[str] = Field(default=None, max_length=50)
    year: Optional[int] = Field(default=None, ge=0, le=2100)
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Особиста оцінка 1-5")

    @field_validator("description", "genre", "year", "rating", mode="before")
    @classmethod
    def clean_blank(cls, v):
        return _blank_to_none(v)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    """Часткове оновлення (PATCH): передай лише ті поля, які треба змінити."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    genre: Optional[str] = Field(default=None, max_length=50)
    year: Optional[int] = Field(default=None, ge=0, le=2100)
    rating: Optional[int] = Field(default=None, ge=1, le=5)

    @field_validator("description", "genre", "year", "rating", mode="before")
    @classmethod
    def clean_blank(cls, v):
        return _blank_to_none(v)

    @field_validator("title", "author")
    @classmethod
    def not_null(cls, v):
        if v is None:
            raise ValueError("Поле не може бути порожнім")
        return v


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: Optional[datetime] = None


class BookPage(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    size: int
    pages: int


class AuthorCount(BaseModel):
    author: str
    books: int


class Stats(BaseModel):
    books: int
    authors: int
    users: int
    avg_rating: Optional[float] = None
    top_authors: List[AuthorCount]
