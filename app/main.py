from app.db.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI()

# 🔥 FORCE CREATE TABLES ON STARTUP
Base.metadata.create_all(bind=engine)

# ✅ CORS MUST BE HERE (before include_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jocular-kelpie-43de9f.netlify.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# ✅ Router AFTER CORS
app.include_router(router)
