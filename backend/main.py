from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as api_router

app = FastAPI(title="Script Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",  # Разрешить все origins через regex
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
