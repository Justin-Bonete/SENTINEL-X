# Build from the repo root: docker build -f apps/api/Dockerfile .
FROM python:3.12-slim
WORKDIR /srv
COPY apps/api/requirements.txt apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt \
 && useradd -m sentinel && mkdir /data && chown sentinel /data
COPY apps apps
WORKDIR /srv/apps/api
USER sentinel
ENV SENTINEL_DB=/data/sentinel.db
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
