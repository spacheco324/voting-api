from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.vote import Vote
from app.schemas.vote import VoteCreate, VoteResponse
from app.schemas.statistics import VotingStatistics
from app.services.voting import cast_vote, get_voting_statistics

router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
)


@router.post(
    "",
    response_model=VoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vote(
    vote_data: VoteCreate,
    db: Session = Depends(get_db),
):
    return cast_vote(vote_data, db)

@router.get(
    "",
    response_model=list[VoteResponse],
)
def get_votes(db: Session = Depends(get_db)):
    return db.scalars(select(Vote)).all()

@router.get(
    "/statistics",
    response_model=VotingStatistics,
)
def get_statistics(db: Session = Depends(get_db)):
    return get_voting_statistics(db)
