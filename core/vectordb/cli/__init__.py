import argparse
import uvicorn

from ..db import VectorDB
from ..api import create_app


def main(argv=None):
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
    args = parser.parse_args(argv)

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
