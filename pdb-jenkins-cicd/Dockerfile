# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the application code into the container
COPY app.py .

# Run the app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]