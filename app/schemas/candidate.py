from pydantic import BaseModel, ConfigDict, Field

class CandidateCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r".*\S.*",
    )
    party: str | None = Field(default=None, max_length=100)

class CandidateResponse(BaseModel):
    id: int
    name: str
    party: str | None
    votes: int

    model_config = ConfigDict(from_attributes=True)
