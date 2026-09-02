from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.voter import Voter
from app.schemas.vote import VoteCreate


def cast_vote(
    vote_data: VoteCreate,
    db: Session,
):
    voter = db.get(Voter, vote_data.voter_id)

    if voter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found.",
        )

    candidate = db.get(Candidate, vote_data.candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found.",
        )

    if voter.has_voted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This voter has already cast a vote.",
        )

    vote = Vote(
        voter_id=voter.id,
        candidate_id=candidate.id,
    )

    voter.has_voted = True
    candidate.votes += 1

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote

def get_voting_statistics(db: Session):
    candidates = db.scalars(
        select(Candidate)
    ).all()

    total_votes = sum(candidate.votes for candidate in candidates)

    total_voters_voted = db.scalar(
        select(func.count())
        .select_from(Voter)
        .where(Voter.has_voted.is_(True))
    )

    results = []

    for candidate in candidates:
        percentage = (
            (candidate.votes / total_votes) * 100
            if total_votes > 0
            else 0
        )

        results.append(
            {
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "votes": candidate.votes,
                "percentage": round(percentage, 2),
            }
        )

    return {
        "total_votes": total_votes,
        "total_voters_voted": total_voters_voted,
        "results": results,
    }