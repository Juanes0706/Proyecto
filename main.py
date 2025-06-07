from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.db import engine  # ajusta la ruta si es diferente
from app.models import Base  # ajusta la ruta según donde estén tus modelos

import home

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(home.router)
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
