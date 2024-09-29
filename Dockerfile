# Dockerfile for FastAPI backend

# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV UVICORN_CMD="uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Run uvicorn server
CMD ["sh", "-c", "$UVICORN_CMD"]
