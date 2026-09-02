from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VoterCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r".*\S.*",
    )
    email: EmailStr
    

class VoterResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    has_voted: bool

    model_config = ConfigDict(from_attributes=True)
    