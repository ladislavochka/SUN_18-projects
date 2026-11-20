from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class AuthorCreate(BaseModel):
    name: str
    biography: str | None = None
    image_name: str | None = None
class AuthorResponse(AuthorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PublisherCreate(BaseModel):
    name: str
    city: str | None = None
class PublisherResponse(PublisherCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class GenreCreate(BaseModel):
    name: str
class GenreResponse(GenreCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookCreate(BaseModel):
    title: str
    year: int | None = None
    pages: int | None = None
    image_name: str | None = None
    author_id: int
    publisher_id: int | None = None
    genre_ids: list[int] = []
class BookResponse(BaseModel):
    id: int
    title: str
    year: int | None
    pages: int | None
    image_name: str | None
    author_id: int
    publisher_id: int | None
    model_config = ConfigDict(from_attributes=True)

class ReaderCreate(BaseModel):
    name: str
    email: EmailStr
class ReaderResponse(ReaderCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BorrowingCreate(BaseModel):
    book_id: int
    reader_id: int
class BorrowingResponse(BaseModel):
    id: int
    book_id: int
    reader_id: int
    borrowed_at: datetime
    returned_at: datetime | None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    id: int
    login: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
