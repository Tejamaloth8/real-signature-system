from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jocular-kelpie-43de9f.netlify.app",
        "https://deft-sundae-d01907.netlify.app"
    ],
    allow_methods=["*"],          # includes OPTIONS
    allow_headers=["*"],          # includes Authorization
    allow_credentials=False
)

