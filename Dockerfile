# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set the PORT environment variable
ENV PORT 8080

# Copy the requirements file
COPY requirements.txt .

# Clear cache and install dependencies to prevent caching issues
RUN pip install --upgrade pip && \
    rm -rf /root/.cache/pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8080

# Command to run the web server using the PORT environment variable
# Note: We use the shell form of CMD to allow for variable substitution.
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --preload -k uvicorn.workers.UvicornWorker main_bot:app
