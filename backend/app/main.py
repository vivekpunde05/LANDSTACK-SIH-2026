from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .routers.analytics import router as analytics_router
from .routers.cases import router as cases_router
from .routers.grievances import router as grievances_router
from .routers.inspections import router as inspections_router
from .routers.parcels import router as parcels_router
from .routers.priorities import router as priorities_router
from .routers.satellite import router as satellite_router
from .services.imagery import DATASET_ROOT, GENERATED_ROOT
from .services.parcels import database_status

settings = get_settings()
app = FastAPI(
    title="LANDSTACK Parcel Intelligence API",
    description="Free/open-source GIS prototype API using synthetic demonstration data.",
    version="0.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(parcels_router)
app.include_router(satellite_router)
app.include_router(priorities_router)
app.include_router(inspections_router)
app.include_router(grievances_router)
app.include_router(cases_router)
app.include_router(analytics_router)
GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/demo-assets", StaticFiles(directory=DATASET_ROOT), name="demo-assets")
app.mount("/generated", StaticFiles(directory=GENERATED_ROOT), name="generated-analysis")


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_request, _error: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": {"code": "database_unavailable", "message": "The parcel database is currently unavailable."}},
    )


@app.get("/api/health", tags=["system"])
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    response = {"status": "ok", "project": settings.project_name, "phase": "9"}
    try:
        response.update(database_status(db))
    except SQLAlchemyError:
        response.update({"status": "degraded", "database": "unavailable"})
    return response





@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "message": "LANDSTACK API is running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health", tags=["system"])
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    response = {"status": "ok", "project": settings.project_name, "phase": "9"}
    try:
        response.update(database_status(db))
    except SQLAlchemyError:
        response.update({"status": "degraded", "database": "unavailable"})
    return response