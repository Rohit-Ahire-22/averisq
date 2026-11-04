from fastapi import FastAPI

from app.api.monitors import router as monitor_router


app = FastAPI(
    title="Averisq API",
    description="API Reliability & Observability Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Welcome to Averisq"}


app.include_router(monitor_router)
