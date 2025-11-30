# Python 3.14.0 Base Image
FROM python:3.14.0-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies and Chromium
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium browser
RUN apt-get update && \
    apt-get install -y chromium chromium-l10n && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright and browsers
RUN playwright install chromium && \
    playwright install-deps

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV CHROME_PATH=/usr/bin/chromium

# Run the application
CMD ["python", "main.py"]
