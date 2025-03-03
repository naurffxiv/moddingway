from fastapi import FastAPI

from moddingway_api.routes import user_router

app = FastAPI(title="Moddingway API")

app.include_router(user_router, tags=["user"])
