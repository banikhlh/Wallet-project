# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from routes.main_view import router as view_router
from routes.api import router as api_router
from core.templates import templates
from database.database import init_db
from dependencies import database
from core.logging_config import logger


logger.info("Запуск приложения")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(database)
    yield
    await database.close_all()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Необработанное исключение: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(view_router)
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)