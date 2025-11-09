from fastapi import FastAPI
from backend.app.api.v1.routes import router as api_router


app = FastAPI(title="Script Generator")

app.include_router(api_router)
