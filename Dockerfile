FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libmagic1 tesseract-ocr tesseract-ocr-all --no-install-recommends

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
