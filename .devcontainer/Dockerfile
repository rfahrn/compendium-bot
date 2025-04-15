# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install apt-based dependencies that Playwright needs
RUN apt-get update && apt-get install -y --no-install-recommends \
  libdbus-1-3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libxkbcommon0 \
  libpango-1.0-0 \
  libcairo2 \
  libasound2 \
  libatspi2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Install Python Playwright + the browser binaries
RUN pip install --no-cache-dir playwright
RUN python -m playwright install

# [Optional] If your project has extra packages:
# copy in requirements.txt BEFORE copying all source for better Docker layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Then copy your code in
WORKDIR /app
COPY . /app
