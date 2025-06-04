import argparse
import json
from pathlib import Path
from typing import List

import hnswlib
from fastapi import FastAPI
from pydantic import BaseModel
from model2vec import StaticModel
import uvicorn

INDEX_PATH = Path("index.bin")
DATA_PATH = Path("data.json")
MODEL_NAME = "cnmoro/Linq-Embed-Mistral-Distilled"


class VectorDB:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = StaticModel.from_pretrained(model_name)
        self.dim = self.model.dim
        self.index = hnswlib.Index(space="cosine", dim=self.dim)
        self.texts: List[str] = []
        if INDEX_PATH.exists() and DATA_PATH.exists():
            self.index.load_index(str(INDEX_PATH))
            self.texts = json.loads(DATA_PATH.read_text())
        else:
            self.index.init_index(max_elements=10000, ef_construction=200, M=16)
        self.index.set_ef(50)

    @staticmethod
    def clear():
        """Delete any persisted index and text data."""
        if INDEX_PATH.exists():
            INDEX_PATH.unlink()
        if DATA_PATH.exists():
            DATA_PATH.unlink()

    def save(self):
        self.index.save_index(str(INDEX_PATH))
        DATA_PATH.write_text(json.dumps(self.texts))

    def add_text(self, text: str):
        self.add_texts([text])

    def add_texts(self, texts: List[str]):
        vecs = self.model.encode(texts)
        start = len(self.texts)
        ids = list(range(start, start + len(texts)))
        self.index.add_items(vecs, ids)
        self.texts.extend(texts)
        self.save()

    def search(self, query: str, k: int = 5):
        vec = self.model.encode([query])[0]
        labels, distances = self.index.knn_query([vec], k=k)
        results = []
        for label, dist in zip(labels[0], distances[0]):
            results.append({"text": self.texts[label], "distance": float(dist)})
        return results


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


def main():
    parser = argparse.ArgumentParser(description="Vector DB CLI")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="remove existing index and data before running",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("serve", help="start REST server")
    add = subparsers.add_parser("add", help="add text")
    add.add_argument("text", help="text to add")
    query = subparsers.add_parser("query", help="query text")
    query.add_argument("text", help="text to query")
    args = parser.parse_args()

    if args.delete:
        VectorDB.clear()

    vdb = VectorDB()

    if args.command == "serve":
        app = create_app(vdb)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif args.command == "add":
        vdb.add_text(args.text)
    elif args.command == "query":
        print(vdb.search(args.text, k=5))


if __name__ == "__main__":
    main()
