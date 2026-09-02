from pydantic import BaseModel, ConfigDict, Field


class VoteCreate(BaseModel):
    voter_id: int = Field(gt=0)
    candidate_id: int = Field(gt=0)


class VoteResponse(BaseModel):
    id: int
    voter_id: int
    candidate_id: int

    model_config = ConfigDict(from_attributes=True)