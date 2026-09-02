from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import Candidate
from app.models.voter import Voter
from app.schemas.candidate import CandidateCreate, CandidateResponse

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)


@router.post(
    "",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db),
):
    existing_voter = db.scalar(
        select(Voter).where(
            func.lower(Voter.name) == candidate_data.name.strip().lower()
        )
    )

    existing_candidate = db.scalar(
        select(Candidate).where(
            func.lower(Candidate.name) == candidate_data.name.strip().lower()
        )
    )

    if existing_voter:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A voter with this name already exists.",
        )

    if existing_candidate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A candidate with this name already exists.",
        )

    candidate = Candidate(
        name=candidate_data.name,
        party=candidate_data.party,
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


@router.get(
    "",
    response_model=list[CandidateResponse],
)
def get_candidates(db: Session = Depends(get_db)):
    return db.scalars(select(Candidate)).all()


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = db.get(Candidate, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found.",
        )

    return candidate


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = db.get(Candidate, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found.",
        )

    if candidate.votes > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A candidate who has received votes cannot be deleted.",
        )

    db.delete(candidate)
    db.commit()