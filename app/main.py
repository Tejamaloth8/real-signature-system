from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.api.auth import router as auth_router
from app.api.files import router as file_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jocular-kelpie-43de9f.netlify.app",
        "https://deft-sundae-d01907.netlify.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False
)

# 🔥 REGISTER ALL ROUTERS (THIS IS THE KEY FIX)
app.include_router(auth_router)
app.include_router(file_router)

# 🔥 CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)
