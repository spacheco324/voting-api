from pydantic import BaseModel


class CandidateStatistics(BaseModel):
    candidate_id: int
    candidate_name: str
    votes: int
    percentage: float


class VotingStatistics(BaseModel):
    total_votes: int
    total_voters_voted: int
    results: list[CandidateStatistics]