from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import diagnoses, webhooks

app = FastAPI(title="Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # MVP: create tables directly from the models. Swap for Alembic
    # migrations once the schema needs to evolve without dropping data.
    Base.metadata.create_all(bind=engine)


app.include_router(diagnoses.router)
app.include_router(webhooks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
