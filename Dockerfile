# Use Ubuntu as base image for better tool compatibility
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/usr/local/go/bin:/root/go/bin
ENV GOPATH=/root/go

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    curl \
    unzip \
    git \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Go (required for some security tools)
RUN wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz

# Create app directory
WORKDIR /app

# Copy all application files
COPY . .

# Verify files and install Python dependencies
RUN echo "=== Listing files ===" && \
    ls -la && \
    echo "=== Contents of requirements.txt ===" && \
    cat requirements.txt && \
    echo "=== Installing Python packages ===" && \
    pip3 install --no-cache-dir -r requirements.txt

# Install security tools
RUN echo "=== Installing security tools ===" && \
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Update Nuclei templates (with error handling)
RUN nuclei -update-templates || echo "Warning: Could not update nuclei templates"

# Create necessary directories
RUN mkdir -p /tmp/scans && \
    chmod 755 /tmp/scans

# Verify tools are installed
RUN echo "=== Verifying tool installation ===" && \
    which subfinder && subfinder -version && \
    which naabu && naabu -version && \
    which nuclei && nuclei -version

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python3", "app.py"]