FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY core ./core
COPY pyproject.toml README.md ./

ENV VECTORDB_HOST=0.0.0.0
ENV VECTORDB_PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "vectordb serve --host $VECTORDB_HOST --port $VECTORDB_PORT"]
