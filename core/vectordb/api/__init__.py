from fastapi import FastAPI
from pydantic import BaseModel

from ..db import VectorDB


def create_app(vdb: VectorDB) -> FastAPI:
    app = FastAPI()

    class Item(BaseModel):
        text: str

    @app.post("/add")
    def add_item(item: Item):
        vdb.add_text(item.text)
        return {"status": "ok"}

    @app.get("/search")
    def search(q: str, k: int = 5):
        return vdb.search(q, k)

    return app
