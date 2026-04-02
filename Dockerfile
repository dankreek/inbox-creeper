# Use Python 3.10+ base image
FROM python:3.11-slim

# Install git and curl
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src

# Install dependencies
RUN uv sync

# Expose port 8000
EXPOSE 8000

# Set environment variables (these should be overridden at runtime)
ENV GOOGLE_CLIENT_ID=""
ENV GOOGLE_CLIENT_SECRET=""
ENV GOOGLE_REFRESH_TOKEN=""

# Run the server
CMD ["uv", "run", "python", "-m", "inbox_creeper.server"]
