from fastapi import Depends, FastAPI, Header, HTTPException, Query
import hmac
from pydantic import BaseModel, constr

from ..db import VectorDB


def create_app(vdb: VectorDB, api_key: str | None = None) -> FastAPI:
    """Create a REST API application for ``vdb``.

    Parameters
    ----------
    vdb:
        Database instance to expose via the API.
    api_key:
        Optional API key required in the ``X-API-Key`` header for all requests.
    """

    app = FastAPI()

    def check_key(x_api_key: str | None = Header(None)) -> None:
        if api_key and not (x_api_key and hmac.compare_digest(x_api_key, api_key)):
            raise HTTPException(status_code=401, detail="invalid API key")

    class Item(BaseModel):
        text: constr(min_length=1)

    @app.post("/add", dependencies=[Depends(check_key)])
    def add_item(item: Item) -> dict[str, str]:
        vdb.add_text(item.text)
        return {"status": "ok"}

    @app.get("/search", dependencies=[Depends(check_key)])
    def search(
        q: constr(min_length=1) = Query(...),
        k: int = Query(5, ge=1),
    ) -> list[dict[str, float | str]]:
        if k > len(vdb.texts):
            raise HTTPException(status_code=400, detail="k exceeds number of stored texts")
        return vdb.search(q, k)

    return app
