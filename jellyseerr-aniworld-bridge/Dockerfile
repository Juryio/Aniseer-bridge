# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install any needed packages specified in pyproject.toml
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

# Run the main application
CMD ["python", "main.py"]
