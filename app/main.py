from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, admin, auth, vote
from .config import settings

# Replaced by alembic
# models.Base.metadata.create_all(bind=engine) 

app = FastAPI()

origins = ["*"] # Configured for public API

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    return {"message": "Stranger API Server"}