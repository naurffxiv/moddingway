import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from moddingway.database import DatabaseConnection
from moddingway_api.routes import user_router, mod_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    create_db_connection()
    yield
    # TODO spin down db connection


def create_db_connection():
    database_connection = DatabaseConnection()
    database_connection.connect()


def configure_logging():
    logging.basicConfig()


app = FastAPI(title="Moddingway API", lifespan=lifespan)
add_pagination(app)

app.include_router(user_router, tags=["user"])
app.include_router(mod_router, tags=["mod"])
