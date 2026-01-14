from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=False,  # 🔴 IMPORTANT: must be False
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
