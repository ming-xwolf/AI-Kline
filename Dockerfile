FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_TIMEOUT=120 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_EXTRA_INDEX_URL=https://pypi.org/simple \
    MPLBACKEND=Agg \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Optional: switch to Tsinghua mirrors for Debian (handle Debian 12 debian.sources)
RUN if [ -f /etc/apt/sources.list ]; then \
      sed -i 's@http://deb.debian.org/debian@https://mirrors.tuna.tsinghua.edu.cn/debian@g' /etc/apt/sources.list && \
      sed -i 's@http://security.debian.org/debian-security@https://mirrors.tuna.tsinghua.edu.cn/debian-security@g' /etc/apt/sources.list; \
    elif [ -f /etc/apt/sources.list.d/debian.sources ]; then \
      sed -i 's@URIs: http://deb.debian.org/debian@URIs: https://mirrors.tuna.tsinghua.edu.cn/debian@g' /etc/apt/sources.list.d/debian.sources && \
      sed -i 's@URIs: http://security.debian.org/debian-security@URIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security@g' /etc/apt/sources.list.d/debian.sources; \
    else \
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    fi

# System deps with retries and timeouts
RUN apt-get update -o Acquire::Retries=5 -o Acquire::http::Timeout=30 && \
    apt-get install -y --no-install-recommends \
      gcc g++ curl build-essential wget netcat-openbsd \
      -o Acquire::Retries=5 -o Acquire::http::Timeout=30 || \
    (apt-get update --fix-missing && \
     apt-get install -y --no-install-recommends \
      gcc g++ curl build-essential wget netcat-openbsd) && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install first for better caching
COPY requirements.txt ./
# Upgrade pip
RUN pip install --upgrade pip

# Install Python deps (use mirrored index + official fallback)
RUN pip install --no-cache-dir --timeout=120 \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt

# Copy source
COPY . .

# Create data/output dirs
RUN mkdir -p /app/data /app/output

# Expose streamable-http port
EXPOSE 8000

# Default to streamable-http server
CMD ["python", "mcp_server.py"]
