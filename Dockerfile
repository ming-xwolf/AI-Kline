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
      unzip gnupg ca-certificates fonts-liberation libasound2 \
      libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 \
      libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 \
      libwayland-client0 libxcomposite1 libxdamage1 libxfixes3 \
      libxkbcommon0 libxrandr2 xdg-utils \
      -o Acquire::Retries=5 -o Acquire::http::Timeout=30 || \
    (apt-get update --fix-missing && \
     apt-get install -y --no-install-recommends \
      gcc g++ curl build-essential wget netcat-openbsd \
      unzip gnupg ca-certificates fonts-liberation libasound2 \
      libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 \
      libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 \
      libwayland-client0 libxcomposite1 libxdamage1 libxfixes3 \
      libxkbcommon0 libxrandr2 xdg-utils) && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome - 自动检测架构
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
        apt-get update && \
        apt-get install -y --no-install-recommends google-chrome-stable && \
        rm -rf /var/lib/apt/lists/* && \
        CHROMEDRIVER_ARCH="linux64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        echo "Installing Chrome for ARM64..." && \
        apt-get update && \
        apt-get install -y --no-install-recommends chromium chromium-driver && \
        ln -s /usr/bin/chromium /usr/bin/google-chrome && \
        ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver && \
        rm -rf /var/lib/apt/lists/* && \
        CHROMEDRIVER_ARCH="linux64"; \
    else \
        echo "Unsupported architecture: $ARCH" && \
        exit 1; \
    fi

# Install ChromeDriver (for amd64 only, arm64 uses chromium-driver)
RUN if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
        CHROME_VERSION=$(google-chrome --version | cut -d " " -f 3 | cut -d "." -f 1) && \
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}") && \
        wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
        unzip /tmp/chromedriver.zip -d /tmp/ && \
        mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
        chmod +x /usr/local/bin/chromedriver && \
        rm -rf /tmp/chromedriver* && \
        chromedriver --version; \
    fi

ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

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
