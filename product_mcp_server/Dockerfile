FROM python:3.12-slim-bookworm

# Logs show up immediately instead of being buffered by Python
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first so this layer is cached:
# rebuilding after a code change won't re-run pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the server code
COPY . .

# Documents the port the REST bridge listens on (informational)
EXPOSE 8001

# rest_api.py is what the backoffice calls over HTTP.
# server.py is the MCP-protocol server and is started by an MCP client, not here.
CMD ["python", "rest_api.py"]
