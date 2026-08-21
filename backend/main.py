from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.auth.routes import router as auth_router
from backend.cases.routes import router as cases_router
from backend.config import get_settings
from backend.database.models import Base
from backend.database.session import engine
from backend.search.routes import router as search_router
from backend.reports.routes import router as reports_router
from backend.age.routes import router as age_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="PehchaanAI API",
    version="0.1.0",
    description="Backend API for missing child identification investigation workflows.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(search_router)
app.include_router(reports_router)
app.include_router(age_router)

# Static image serving:
#   /uploads     -> uploaded case query photos
#   /ref-images  -> reference corpus images (e.g. FGNET/images)
app.mount("/uploads", StaticFiles(directory="uploads", check_dir=False), name="uploads")
app.mount(
    "/ref-images",
    StaticFiles(directory=Path(settings.ref_images_dir), check_dir=False),
    name="ref-images",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
