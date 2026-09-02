from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    voter_id: Mapped[int] = mapped_column(
        ForeignKey("voters.id"),
        nullable=False,
        unique=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
    )

    voter: Mapped["Voter"] = relationship(
        back_populates="votes",
    )

    candidate: Mapped["Candidate"] = relationship(
        back_populates="vote_records",
    )