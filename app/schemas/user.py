from pydantic import BaseModel


class UserSimple(BaseModel):

    id: int

    email: str

    class Config:

        from_attributes = True