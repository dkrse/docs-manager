FROM python:3.12-slim

WORKDIR /opt/apps/document-manager

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/thumbnails && chmod -R 777 uploads

EXPOSE 5214

CMD ["python", "run.py"]
