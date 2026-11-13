from fastapi import FastAPI

from app.api.monitors import router as monitor_router
from app.api.auth import router as auth_router


app = FastAPI(
    title="Averisq API",
    description="API Reliability & Observability Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Welcome to Averisq"}


app.include_router(monitor_router)
app.include_router(auth_router)
