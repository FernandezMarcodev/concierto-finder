FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"

# Aplica las migraciones pendientes y recién después levanta la API.
# `flask --app app` usa create_app() y no arranca las tareas en background.
CMD ["sh", "-c", "flask --app app db upgrade && exec waitress-serve --host=0.0.0.0 --port=8000 app.main:app"]