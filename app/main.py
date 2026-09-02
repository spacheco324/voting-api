from fastapi import FastAPI

from app.database import Base, engine
from app.models import Candidate, Vote, Voter
from app.routers.voters import router as voters_router
from app.routers.candidates import router as candidates_router
from app.routers.votes import router as votes_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voting API",
    description="RESTful API for a voting system.",
    version="1.0.0",
)

app.include_router(voters_router)
app.include_router(candidates_router)
app.include_router(votes_router)

@app.get("/")
def root():
    return {"message": "Voting API is running"}