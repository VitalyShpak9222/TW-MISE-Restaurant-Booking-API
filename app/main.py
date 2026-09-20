from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles
from app.api.bookings import router as bookings_router
from app.core.config import settings
from app.db import init_db

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield

def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        redoc_url=None,
    )

    application.mount("/static", StaticFiles(directory="app/static"), name="static")

    @application.get("/redoc", include_in_schema=False)
    async def custom_redoc():
        return get_redoc_html(
            openapi_url=application.openapi_url,
            title=f"{application.title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )

    application.include_router(bookings_router)
    return application

app = create_app()