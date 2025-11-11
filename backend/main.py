from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as api_router

app = FastAPI(title="Script Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", 
                   "https://storyteller-monorepo.vercel.app", 
                   "https://storyteller-monorepo.onrender.com",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

app.include_router(api_router, prefix="/api/v1")
