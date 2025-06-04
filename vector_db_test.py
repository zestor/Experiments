from vector_db import VectorDB, INDEX_PATH, DATA_PATH
import os


def main():
    if INDEX_PATH.exists():
        os.remove(INDEX_PATH)
    if DATA_PATH.exists():
        os.remove(DATA_PATH)
    vdb = VectorDB()
    # generate 1000 sentences
    sentences = [f"This is sample sentence {i}" for i in range(1000)]
    vdb.add_texts(sentences)
    query = sentences[42]
    results = vdb.search(query, k=1)
    print("Query:", query)
    print("Top result:", results[0])


if __name__ == "__main__":
    main()
