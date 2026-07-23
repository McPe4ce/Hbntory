FROM python:3.12-slim-bookworm

# Logs show up immediately instead of being buffered by Python
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first so this layer is cached:
# rebuilding after a code change won't re-run pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app code
COPY . .

# Documents the port Flask listens on (informational)
EXPOSE 5000

CMD ["python", "run.py"]
