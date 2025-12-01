# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Update pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8080

# Command to run the web server using Gunicorn with a Uvicorn worker for asyncio support.
# --preload is used to ensure the APScheduler is started only once in the master process.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--preload", "-k", "uvicorn.workers.UvicornWorker", "main_bot:app"]
