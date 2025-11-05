# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Create a user and group to run the application
RUN groupadd -r appgroup && useradd --no-create-home -r -g appgroup appuser

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Use --chown to set the owner of the copied files to the non-root user
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Define environment variable
ENV PORT 8080

# Run the application
CMD ["python", "app.py"]