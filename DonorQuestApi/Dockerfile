# Step 1: Use official Python base image
FROM python:3.11-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy source code
COPY . .

# Step 5: Expose FastAPI default port
EXPOSE 8000

# Step 6: Run app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]