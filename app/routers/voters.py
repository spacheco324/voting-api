from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.voter import Voter
from app.models.candidate import Candidate
from app.schemas.voter import VoterCreate, VoterResponse

router = APIRouter(
    prefix="/voters",
    tags=["Voters"],
)


@router.post(
    "",
    response_model=VoterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_voter(
    voter_data: VoterCreate,
    db: Session = Depends(get_db),
):
    existing_voter = db.scalar(
        select(Voter).where(Voter.email == voter_data.email)
    )

    existing_candidate = db.scalar(
        select(Candidate).where(
            func.lower(Candidate.name) == voter_data.name.strip().lower()
        )
    )

    if existing_voter:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A voter with this email already exists.",
        )

    if existing_candidate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This person is already registered as a candidate.",
        )

    voter = Voter(
        name=voter_data.name.strip(),
        email=voter_data.email,
    )

    db.add(voter)
    db.commit()
    db.refresh(voter)

    return voter


@router.get(
    "",
    response_model=list[VoterResponse],
)
def get_voters(db: Session = Depends(get_db)):
    return db.scalars(select(Voter)).all()


@router.get(
    "/{voter_id}",
    response_model=VoterResponse,
)
def get_voter(
    voter_id: int,
    db: Session = Depends(get_db),
):
    voter = db.get(Voter, voter_id)

    if voter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found.",
        )

    return voter


@router.delete(
    "/{voter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_voter(
    voter_id: int,
    db: Session = Depends(get_db),
):
    voter = db.get(Voter, voter_id)

    if voter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found.",
        )

    if voter.has_voted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A voter who has already voted cannot be deleted.",
        )

    db.delete(voter)
    db.commit()