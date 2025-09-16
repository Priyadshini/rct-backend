# Dockerfile

FROM python:3.10-slim

WORKDIR /src

# Copy dependency files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of source
COPY app.py .
COPY src ./src
# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app:create_app", "--host", "0.0.0.0", "--port", "8000"]
