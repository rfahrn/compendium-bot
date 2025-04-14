# .devcontainer/Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.51.0-focal

# Copy in your code (optional if you just mount the repo)
WORKDIR /app
COPY . /app

# Example: install your Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Done! The base image already has Python, Playwright, and the browsers
