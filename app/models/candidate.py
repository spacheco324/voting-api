from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    party: Mapped[str | None] = mapped_column(String(100), nullable=True)
    votes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    vote_records: Mapped[list["Vote"]] = relationship(
        back_populates="candidate",
    )