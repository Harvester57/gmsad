# Stage 1: Build stage
FROM python:3.14-slim@sha256:b877e50bd90de10af8d82c57a022fc2e0dc731c5320d762a27986facfc3355c1 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libkrb5-dev \
    krb5-user \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy pyproject.toml and source to build wheels
COPY pyproject.toml README.md ./
COPY gmsad/ ./gmsad/

RUN pip wheel --no-cache-dir --wheel-dir /build/wheels .

# Stage 2: Runtime stage
FROM python:3.14-slim@sha256:b877e50bd90de10af8d82c57a022fc2e0dc731c5320d762a27986facfc3355c1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libkrb5-3 \
    krb5-user \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built wheels from builder stage
COPY --from=builder /build/wheels /app/wheels
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels gmsad && rm -rf /app/wheels

# Default configuration path
ENV GMSAD_CONFIG=/etc/gmsad/gmsad.conf

ENTRYPOINT ["gmsad"]
CMD ["-c", "/etc/gmsad/gmsad.conf"]
