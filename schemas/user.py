from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(...)


class UserShortResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
