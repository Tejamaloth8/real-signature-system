from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api.routes import router

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

# 🔥 REGISTER ROUTES (THIS WAS MISSING)
app.include_router(router)

# 🔥 CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)
